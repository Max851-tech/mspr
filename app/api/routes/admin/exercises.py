"""Admin endpoints for exercise CRUD operations with audit trail."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.admin_auth import require_admin_api_key
from app.api.dependencies.database import get_db
from app.exceptions.exercise import ExerciseAlreadyExists, ExerciseNotFound
from app.models.exercice import Exercice
from app.schemas.bulk import (
    BulkAction,
    BulkItemResult,
    BulkRequest,
    BulkResponse,
)
from app.schemas.common import ResponseWithWarnings, Warning
from app.schemas.exercise import ExerciseCreate, ExerciseRead, ExerciseUpdate
from app.services.audit import AuditService
from app.services.validation import LenientValidator, Warning as ValidationWarning

router = APIRouter(
    prefix="/api/v1/admin/exercises",
    tags=["admin-exercises"],
    dependencies=[Depends(require_admin_api_key)],
    responses={
        404: {"description": "Exercise not found"},
        409: {"description": "Exercise already exists"},
    },
)


@router.post(
    "",
    response_model=ResponseWithWarnings[ExerciseRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new exercise",
    description="Create a new exercise with validation warnings. Returns warnings for missing or suspicious data.",
)
async def create_exercise(
    exercise_data: ExerciseCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResponseWithWarnings[ExerciseRead]:
    """Create a new exercise.

    Returns:
        ResponseWithWarnings with created exercise and validation warnings

    Raises:
        ExerciseAlreadyExists: If exercise with same name already exists
    """
    # Validate and normalize data
    validator = LenientValidator()
    cleaned_data, validation_warnings = validator.validate_exercise(
        exercise_data.model_dump(exclude_unset=True)
    )

    # Check for duplicate nom (including soft-deleted)
    existing = await db.execute(
        select(Exercice).where(Exercice.nom == cleaned_data["nom"])
    )
    existing_exercise = existing.scalar_one_or_none()
    if existing_exercise:
        if existing_exercise.is_deleted:
            # Warn but allow creation
            validation_warnings.append(
                ValidationWarning(
                    field="nom",
                    message=f"A deleted exercise with name '{cleaned_data['nom']}' exists. Consider restoring instead.",
                    code="DUPLICATE_DELETED",
                )
            )
        else:
            # Hard error for active duplicate
            raise ExerciseAlreadyExists(cleaned_data["nom"])

    # Create exercise
    exercise = Exercice(**cleaned_data)
    db.add(exercise)
    await db.flush()  # Get ID for audit log

    # Log creation
    audit_service = AuditService(db)
    await audit_service.log_insert(exercise)

    await db.commit()
    await db.refresh(exercise)

    # Convert validation warnings to schema warnings
    warnings = [
        Warning(field=w.field, message=w.message, code=w.code)
        for w in validation_warnings
    ]

    return ResponseWithWarnings(data=exercise, warnings=warnings)


@router.get(
    "/{exercise_id}",
    response_model=ExerciseRead,
    summary="Get exercise by ID (admin)",
    description="Returns a single exercise by ID. Unlike public endpoint, returns soft-deleted items.",
)
async def get_exercise_admin(
    exercise_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExerciseRead:
    """Get a single exercise by ID (admin can see deleted).

    Returns:
        ExerciseRead schema

    Raises:
        ExerciseNotFound: If exercise doesn't exist
    """
    result = await db.execute(
        select(Exercice).where(Exercice.exercice_id == exercise_id)
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise ExerciseNotFound(exercise_id)
    return exercise


@router.put(
    "/{exercise_id}",
    response_model=ResponseWithWarnings[ExerciseRead],
    summary="Update exercise",
    description="Update exercise fields. Only provided fields are updated. Returns validation warnings.",
)
async def update_exercise(
    exercise_id: int,
    exercise_data: ExerciseUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResponseWithWarnings[ExerciseRead]:
    """Update exercise fields.

    Returns:
        ResponseWithWarnings with updated exercise and validation warnings

    Raises:
        ExerciseNotFound: If exercise doesn't exist
    """
    # Get existing exercise
    result = await db.execute(
        select(Exercice).where(Exercice.exercice_id == exercise_id)
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise ExerciseNotFound(exercise_id)

    # Capture old values for audit
    audit_service = AuditService(db)
    old_values = audit_service.get_model_dict(exercise)

    # Validate and normalize update data
    validator = LenientValidator()
    update_dict = exercise_data.model_dump(exclude_unset=True)
    if update_dict:
        cleaned_data, validation_warnings = validator.validate_exercise(update_dict)

        # Apply updates
        for field, value in cleaned_data.items():
            setattr(exercise, field, value)

        # Log update
        await audit_service.log_update(exercise, old_values)

        await db.commit()
        await db.refresh(exercise)

        # Convert validation warnings
        warnings = [
            Warning(field=w.field, message=w.message, code=w.code)
            for w in validation_warnings
        ]
    else:
        warnings = []

    return ResponseWithWarnings(data=exercise, warnings=warnings)


@router.delete(
    "/{exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete exercise",
    description="Soft deletes an exercise by setting deleted_at timestamp. Can be restored later.",
)
async def delete_exercise(
    exercise_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft delete an exercise.

    Raises:
        ExerciseNotFound: If exercise doesn't exist
    """
    # Get existing exercise
    result = await db.execute(
        select(Exercice).where(Exercice.exercice_id == exercise_id)
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise ExerciseNotFound(exercise_id)

    # Soft delete
    exercise.soft_delete()

    # Log deletion
    audit_service = AuditService(db)
    await audit_service.log_delete(exercise)

    await db.commit()


@router.post(
    "/{exercise_id}/restore",
    response_model=ExerciseRead,
    summary="Restore soft-deleted exercise",
    description="Restores a soft-deleted exercise by clearing deleted_at timestamp.",
)
async def restore_exercise(
    exercise_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExerciseRead:
    """Restore a soft-deleted exercise.

    Returns:
        Restored exercise

    Raises:
        ExerciseNotFound: If exercise doesn't exist or is not deleted
    """
    # Get exercise
    result = await db.execute(
        select(Exercice).where(Exercice.exercice_id == exercise_id)
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise ExerciseNotFound(exercise_id)

    if not exercise.is_deleted:
        raise ExerciseNotFound(exercise_id)  # Not deleted, treat as not found

    # Restore
    exercise.restore()

    # Log restore
    audit_service = AuditService(db)
    await audit_service.log_restore(exercise)

    await db.commit()
    await db.refresh(exercise)

    return exercise


@router.post(
    "/bulk",
    response_model=BulkResponse,
    summary="Bulk exercise operations",
    description="Process multiple CREATE, UPDATE, or DELETE operations in a single request.",
)
async def bulk_exercises(
    bulk_request: BulkRequest[ExerciseCreate],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BulkResponse:
    """Process bulk exercise operations.

    Each item is processed independently. Failures are captured per-item.
    Transaction is committed only if all operations succeed.

    Returns:
        BulkResponse with per-item results
    """
    results: list[BulkItemResult] = []
    succeeded = 0
    failed = 0

    audit_service = AuditService(db)
    validator = LenientValidator()

    for index, item in enumerate(bulk_request.items):
        try:
            if item.action == BulkAction.CREATE:
                # Create operation
                if not item.data:
                    raise ValueError("data is required for CREATE action")

                cleaned_data, validation_warnings = validator.validate_exercise(
                    item.data.model_dump(exclude_unset=True)
                )

                # Check duplicate
                existing = await db.execute(
                    select(Exercice).where(Exercice.nom == cleaned_data["nom"])
                )
                if existing.scalar_one_or_none():
                    raise ValueError(f"Exercise with name '{cleaned_data['nom']}' already exists")

                exercise = Exercice(**cleaned_data)
                db.add(exercise)
                await db.flush()
                await audit_service.log_insert(exercise)

                results.append(
                    BulkItemResult(
                        index=index,
                        success=True,
                        id=exercise.exercice_id,
                        warnings=[w.message for w in validation_warnings],
                    )
                )
                succeeded += 1

            elif item.action == BulkAction.UPDATE:
                # Update operation
                if not item.id:
                    raise ValueError("id is required for UPDATE action")
                if not item.data:
                    raise ValueError("data is required for UPDATE action")

                result = await db.execute(
                    select(Exercice).where(Exercice.exercice_id == item.id)
                )
                exercise = result.scalar_one_or_none()
                if not exercise:
                    raise ValueError(f"Exercise with id {item.id} not found")

                old_values = audit_service.get_model_dict(exercise)
                cleaned_data, validation_warnings = validator.validate_exercise(
                    item.data.model_dump(exclude_unset=True)
                )

                for field, value in cleaned_data.items():
                    setattr(exercise, field, value)

                await db.flush()
                await audit_service.log_update(exercise, old_values)

                results.append(
                    BulkItemResult(
                        index=index,
                        success=True,
                        id=exercise.exercice_id,
                        warnings=[w.message for w in validation_warnings],
                    )
                )
                succeeded += 1

            elif item.action == BulkAction.DELETE:
                # Delete operation
                if not item.id:
                    raise ValueError("id is required for DELETE action")

                result = await db.execute(
                    select(Exercice).where(Exercice.exercice_id == item.id)
                )
                exercise = result.scalar_one_or_none()
                if not exercise:
                    raise ValueError(f"Exercise with id {item.id} not found")

                exercise.soft_delete()
                await db.flush()
                await audit_service.log_delete(exercise)

                results.append(
                    BulkItemResult(
                        index=index,
                        success=True,
                        id=exercise.exercice_id,
                    )
                )
                succeeded += 1

        except Exception as e:
            results.append(
                BulkItemResult(
                    index=index,
                    success=False,
                    error=str(e),
                )
            )
            failed += 1

    # Commit all operations
    await db.commit()

    return BulkResponse(
        total=len(bulk_request.items),
        succeeded=succeeded,
        failed=failed,
        results=results,
    )


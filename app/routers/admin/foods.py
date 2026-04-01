"""Admin endpoints for food CRUD operations with audit trail."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.exceptions.food import FoodAlreadyExists, FoodNotFound
from app.models.aliment import Aliment
from app.schemas.bulk import (
    BulkAction,
    BulkItem,
    BulkItemResult,
    BulkRequest,
    BulkResponse,
)
from app.schemas.common import ResponseWithWarnings, Warning
from app.schemas.food import FoodCreate, FoodRead, FoodUpdate
from app.services.audit import AuditService
from app.services.validation import LenientValidator, Warning as ValidationWarning

router = APIRouter(
    prefix="/api/v1/admin/foods",
    tags=["admin-foods"],
    responses={
        404: {"description": "Food not found"},
        409: {"description": "Food already exists"},
    },
)


@router.post(
    "",
    response_model=ResponseWithWarnings[FoodRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new food",
    description="Create a new food item with validation warnings. Returns warnings for missing or suspicious data.",
)
async def create_food(
    food_data: FoodCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResponseWithWarnings[FoodRead]:
    """Create a new food item.

    Returns:
        ResponseWithWarnings with created food and validation warnings

    Raises:
        FoodAlreadyExists: If food with same name already exists
    """
    # Validate and normalize data
    validator = LenientValidator()
    cleaned_data, validation_warnings = validator.validate_food(
        food_data.model_dump(exclude_unset=True)
    )

    # Check for duplicate nom (including soft-deleted)
    existing = await db.execute(
        select(Aliment).where(Aliment.nom == cleaned_data["nom"])
    )
    existing_food = existing.scalar_one_or_none()
    if existing_food:
        if existing_food.is_deleted:
            # Warn but allow creation
            validation_warnings.append(
                ValidationWarning(
                    field="nom",
                    message=f"A deleted food with name '{cleaned_data['nom']}' exists. Consider restoring instead.",
                    code="DUPLICATE_DELETED",
                )
            )
        else:
            # Hard error for active duplicate
            raise FoodAlreadyExists(cleaned_data["nom"])

    # Create food
    food = Aliment(**cleaned_data)
    db.add(food)
    await db.flush()  # Get ID for audit log

    # Log creation
    audit_service = AuditService(db)
    await audit_service.log_insert(food)

    await db.commit()
    await db.refresh(food)

    # Convert validation warnings to schema warnings
    warnings = [
        Warning(field=w.field, message=w.message, code=w.code)
        for w in validation_warnings
    ]

    return ResponseWithWarnings(data=food, warnings=warnings)


@router.get(
    "/{food_id}",
    response_model=FoodRead,
    summary="Get food by ID (admin)",
    description="Returns a single food item by ID. Unlike public endpoint, returns soft-deleted items.",
)
async def get_food_admin(
    food_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FoodRead:
    """Get a single food by ID (admin can see deleted).

    Returns:
        FoodRead schema

    Raises:
        FoodNotFound: If food doesn't exist
    """
    result = await db.execute(
        select(Aliment).where(Aliment.aliment_id == food_id)
    )
    food = result.scalar_one_or_none()
    if not food:
        raise FoodNotFound(food_id)
    return food


@router.put(
    "/{food_id}",
    response_model=ResponseWithWarnings[FoodRead],
    summary="Update food",
    description="Update food fields. Only provided fields are updated. Returns validation warnings.",
)
async def update_food(
    food_id: int,
    food_data: FoodUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResponseWithWarnings[FoodRead]:
    """Update food fields.

    Returns:
        ResponseWithWarnings with updated food and validation warnings

    Raises:
        FoodNotFound: If food doesn't exist
    """
    # Get existing food
    result = await db.execute(
        select(Aliment).where(Aliment.aliment_id == food_id)
    )
    food = result.scalar_one_or_none()
    if not food:
        raise FoodNotFound(food_id)

    # Capture old values for audit
    audit_service = AuditService(db)
    old_values = audit_service.get_model_dict(food)

    # Validate and normalize update data
    validator = LenientValidator()
    update_dict = food_data.model_dump(exclude_unset=True)
    if update_dict:
        cleaned_data, validation_warnings = validator.validate_food(update_dict)

        # Apply updates
        for field, value in cleaned_data.items():
            setattr(food, field, value)

        # Log update
        await audit_service.log_update(food, old_values)

        await db.commit()
        await db.refresh(food)

        # Convert validation warnings
        warnings = [
            Warning(field=w.field, message=w.message, code=w.code)
            for w in validation_warnings
        ]
    else:
        warnings = []

    return ResponseWithWarnings(data=food, warnings=warnings)


@router.delete(
    "/{food_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete food",
    description="Soft deletes a food item by setting deleted_at timestamp. Can be restored later.",
)
async def delete_food(
    food_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft delete a food item.

    Raises:
        FoodNotFound: If food doesn't exist
    """
    # Get existing food
    result = await db.execute(
        select(Aliment).where(Aliment.aliment_id == food_id)
    )
    food = result.scalar_one_or_none()
    if not food:
        raise FoodNotFound(food_id)

    # Soft delete
    food.soft_delete()

    # Log deletion
    audit_service = AuditService(db)
    await audit_service.log_delete(food)

    await db.commit()


@router.post(
    "/{food_id}/restore",
    response_model=FoodRead,
    summary="Restore soft-deleted food",
    description="Restores a soft-deleted food item by clearing deleted_at timestamp.",
)
async def restore_food(
    food_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FoodRead:
    """Restore a soft-deleted food.

    Returns:
        Restored food

    Raises:
        FoodNotFound: If food doesn't exist or is not deleted
    """
    # Get food
    result = await db.execute(
        select(Aliment).where(Aliment.aliment_id == food_id)
    )
    food = result.scalar_one_or_none()
    if not food:
        raise FoodNotFound(food_id)

    if not food.is_deleted:
        raise FoodNotFound(food_id)  # Not deleted, treat as not found

    # Restore
    food.restore()

    # Log restore
    audit_service = AuditService(db)
    await audit_service.log_restore(food)

    await db.commit()
    await db.refresh(food)

    return food


@router.post(
    "/bulk",
    response_model=BulkResponse,
    summary="Bulk food operations",
    description="Process multiple CREATE, UPDATE, or DELETE operations in a single request.",
)
async def bulk_foods(
    bulk_request: BulkRequest[FoodCreate],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BulkResponse:
    """Process bulk food operations.

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

                cleaned_data, validation_warnings = validator.validate_food(
                    item.data.model_dump(exclude_unset=True)
                )

                # Check duplicate
                existing = await db.execute(
                    select(Aliment).where(Aliment.nom == cleaned_data["nom"])
                )
                if existing.scalar_one_or_none():
                    raise ValueError(f"Food with name '{cleaned_data['nom']}' already exists")

                food = Aliment(**cleaned_data)
                db.add(food)
                await db.flush()
                await audit_service.log_insert(food)

                results.append(
                    BulkItemResult(
                        index=index,
                        success=True,
                        id=food.aliment_id,
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
                    select(Aliment).where(Aliment.aliment_id == item.id)
                )
                food = result.scalar_one_or_none()
                if not food:
                    raise ValueError(f"Food with id {item.id} not found")

                old_values = audit_service.get_model_dict(food)
                cleaned_data, validation_warnings = validator.validate_food(
                    item.data.model_dump(exclude_unset=True)
                )

                for field, value in cleaned_data.items():
                    setattr(food, field, value)

                await db.flush()
                await audit_service.log_update(food, old_values)

                results.append(
                    BulkItemResult(
                        index=index,
                        success=True,
                        id=food.aliment_id,
                        warnings=[w.message for w in validation_warnings],
                    )
                )
                succeeded += 1

            elif item.action == BulkAction.DELETE:
                # Delete operation
                if not item.id:
                    raise ValueError("id is required for DELETE action")

                result = await db.execute(
                    select(Aliment).where(Aliment.aliment_id == item.id)
                )
                food = result.scalar_one_or_none()
                if not food:
                    raise ValueError(f"Food with id {item.id} not found")

                food.soft_delete()
                await db.flush()
                await audit_service.log_delete(food)

                results.append(
                    BulkItemResult(
                        index=index,
                        success=True,
                        id=food.aliment_id,
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

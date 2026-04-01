"""Lenient validation service with warnings instead of errors."""
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class Warning:
    """Validation warning (non-blocking)."""

    field: str
    message: str
    code: str


class LenientValidator:
    """Validator that normalizes data and returns warnings instead of hard errors.

    Accepts partial/imperfect data, cleans it, and warns about potential issues.
    """

    def validate_food(self, data: dict[str, Any]) -> tuple[dict[str, Any], list[Warning]]:
        """Validate and normalize food data.

        Args:
            data: Raw food data dictionary

        Returns:
            Tuple of (cleaned_data, warnings)
        """
        warnings: list[Warning] = []
        cleaned: dict[str, Any] = data.copy()

        # Normalize nom (required field)
        if "nom" in cleaned and cleaned["nom"]:
            cleaned["nom"] = str(cleaned["nom"]).strip()
            if not cleaned["nom"]:
                warnings.append(
                    Warning(
                        field="nom",
                        message="Food name is empty after normalization",
                        code="EMPTY_NAME",
                    )
                )

        # Normalize categorie (optional)
        if "categorie" in cleaned and cleaned["categorie"]:
            cleaned["categorie"] = str(cleaned["categorie"]).strip().lower()

        # Check for recommended fields
        if "calories_kcal" not in cleaned or cleaned["calories_kcal"] is None:
            warnings.append(
                Warning(
                    field="calories_kcal",
                    message="Calories not provided - recommended for nutritional tracking",
                    code="MISSING_CALORIES",
                )
            )

        # Check for suspicious values
        if "calories_kcal" in cleaned and cleaned["calories_kcal"] is not None:
            calories = float(cleaned["calories_kcal"])
            if calories > 1000:
                warnings.append(
                    Warning(
                        field="calories_kcal",
                        message=f"Unusually high calorie value: {calories} kcal",
                        code="SUSPICIOUS_CALORIES",
                    )
                )
            elif calories < 0:
                warnings.append(
                    Warning(
                        field="calories_kcal",
                        message="Negative calorie value is invalid",
                        code="NEGATIVE_CALORIES",
                    )
                )

        # Check protein values
        if "proteines_g" in cleaned and cleaned["proteines_g"] is not None:
            proteines = float(cleaned["proteines_g"])
            if proteines < 0:
                warnings.append(
                    Warning(
                        field="proteines_g",
                        message="Negative protein value is invalid",
                        code="NEGATIVE_PROTEIN",
                    )
                )

        # Check carbs values
        if "glucides_g" in cleaned and cleaned["glucides_g"] is not None:
            glucides = float(cleaned["glucides_g"])
            if glucides < 0:
                warnings.append(
                    Warning(
                        field="glucides_g",
                        message="Negative carbs value is invalid",
                        code="NEGATIVE_CARBS",
                    )
                )

        # Check fat values
        if "lipides_g" in cleaned and cleaned["lipides_g"] is not None:
            lipides = float(cleaned["lipides_g"])
            if lipides < 0:
                warnings.append(
                    Warning(
                        field="lipides_g",
                        message="Negative fat value is invalid",
                        code="NEGATIVE_FAT",
                    )
                )

        return cleaned, warnings

    def validate_exercise(self, data: dict[str, Any]) -> tuple[dict[str, Any], list[Warning]]:
        """Validate and normalize exercise data.

        Args:
            data: Raw exercise data dictionary

        Returns:
            Tuple of (cleaned_data, warnings)
        """
        warnings: list[Warning] = []
        cleaned: dict[str, Any] = data.copy()

        # Normalize nom (required field)
        if "nom" in cleaned and cleaned["nom"]:
            cleaned["nom"] = str(cleaned["nom"]).strip()
            if not cleaned["nom"]:
                warnings.append(
                    Warning(
                        field="nom",
                        message="Exercise name is empty after normalization",
                        code="EMPTY_NAME",
                    )
                )

        # Normalize muscle_cible (optional)
        if "muscle_cible" in cleaned and cleaned["muscle_cible"]:
            cleaned["muscle_cible"] = str(cleaned["muscle_cible"]).strip().lower()

        # Normalize equipement (optional)
        if "equipement" in cleaned and cleaned["equipement"]:
            cleaned["equipement"] = str(cleaned["equipement"]).strip().lower()

        # Normalize difficulte (optional) - keep uppercase for enum matching
        if "difficulte" in cleaned and cleaned["difficulte"]:
            # If it's a DifficultyLevel enum, extract value
            if hasattr(cleaned["difficulte"], "value"):
                cleaned["difficulte"] = cleaned["difficulte"].value
            else:
                cleaned["difficulte"] = str(cleaned["difficulte"]).upper()

        # Check for recommended fields
        if "muscle_cible" not in cleaned or cleaned["muscle_cible"] is None:
            warnings.append(
                Warning(
                    field="muscle_cible",
                    message="Target muscle not provided - recommended for exercise categorization",
                    code="MISSING_MUSCLE",
                )
            )

        if "difficulte" not in cleaned or cleaned["difficulte"] is None:
            warnings.append(
                Warning(
                    field="difficulte",
                    message="Difficulty level not provided - recommended for user filtering",
                    code="MISSING_DIFFICULTY",
                )
            )

        return cleaned, warnings

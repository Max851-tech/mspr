"""Unit tests for tracking service helpers."""
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.objectif_utilisateur import ObjectifUtilisateur  # noqa: E402
from app.services.tracking import TrackingService  # noqa: E402


class TrackingServiceTestCase(unittest.IsolatedAsyncioTestCase):
    """Cover the core business rule for active objectives."""

    async def test_deactivate_other_objectives_keeps_selected_objective_active(self) -> None:
        first = ObjectifUtilisateur(
            objectif_id=1,
            utilisateur_id=10,
            date_debut="2026-01-01",
            actif_unique=True,
        )
        second = ObjectifUtilisateur(
            objectif_id=2,
            utilisateur_id=10,
            date_debut="2026-02-01",
            actif_unique=True,
        )

        execute_result = MagicMock()
        execute_result.scalars.return_value = [first, second]

        db = AsyncMock()
        db.execute.return_value = execute_result

        service = TrackingService(db)
        await service.deactivate_other_objectives(user_id=10, keep_objective_id=2)

        self.assertFalse(first.actif_unique)
        self.assertTrue(second.actif_unique)
        db.execute.assert_awaited_once()

"""Smoke tests for application wiring."""
import sys
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


class AppRoutesTestCase(unittest.TestCase):
    """Verify the FastAPI app exposes the expected tracking endpoints."""

    def test_tracking_routes_are_registered(self) -> None:
        route_paths = {route.path for route in app.routes}

        self.assertIn("/api/v1/users/{user_id}/objectives", route_paths)
        self.assertIn("/api/v1/users/{user_id}/objectives/{objective_id}", route_paths)
        self.assertIn("/api/v1/users/{user_id}/progress-photos", route_paths)
        self.assertIn("/api/v1/users/{user_id}/progress-photos/{photo_id}", route_paths)

"""Unit and integration tests for Guided Demo Mode progression."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import require_roles
from backend.app.services.demo.engine import start_demo_presentation, progress_next, progress_previous, get_current_demo_status
from backend.app.services.demo.state import reset_demo_state


class TestDemoStateAndNavigation(unittest.TestCase):
    def setUp(self) -> None:
        reset_demo_state()

    def test_start_demo_default(self) -> None:
        res = start_demo_presentation("burglary", "manual")
        self.assertEqual(res["step_index"], 0)
        self.assertEqual(res["scenario_id"], "burglary")
        self.assertTrue(res["is_playing"])

    def test_next_and_previous(self) -> None:
        start_demo_presentation("burglary", "manual")
        res = progress_next()
        self.assertEqual(res["step_index"], 1)
        
        res = progress_previous()
        self.assertEqual(res["step_index"], 0)


class TestDemoAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.app = app
        app.dependency_overrides[require_roles("analyst", "supervisor", "admin")] = lambda: {"username": "test-user", "role": "analyst"}
        reset_demo_state()

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_api_start_demo(self) -> None:
        response = self.client.get("/api/demo/start?scenario=burglary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["step_index"], 0)
        self.assertEqual(data["scenario_id"], "burglary")

    def test_api_navigation_next(self) -> None:
        self.client.get("/api/demo/start?scenario=burglary")
        response = self.client.get("/api/demo/next")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["step_index"], 1)
        
        # Test status endpoint
        response_status = self.client.get("/api/demo/status")
        self.assertEqual(response_status.status_code, 200)
        self.assertEqual(response_status.json()["step_index"], 1)


if __name__ == "__main__":
    unittest.main()

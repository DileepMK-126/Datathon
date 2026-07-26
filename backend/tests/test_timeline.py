"""Unit and API integration tests for the Investigation Timeline engine, builders, and routers."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import require_roles
from backend.app.services.timeline.builder import make_event_id, build_timeline
from backend.app.services.timeline.engine import get_case_timeline


class TestTimelineBuilder(unittest.TestCase):
    def test_make_event_id_deterministic(self) -> None:
        """Verify event ID hashing generates deterministic keys."""
        id1 = make_event_id("case-1", "type", "2026-07-26T06:00:00Z")
        id2 = make_event_id("case-1", "type", "2026-07-26T06:00:00Z")
        self.assertEqual(id1, id2)
        self.assertTrue(id1.startswith("EVT-"))

    def test_build_timeline_invalid_case(self) -> None:
        """Verify that building a timeline for an unknown case returns an empty event list."""
        events = build_timeline("invalid-case-id")
        self.assertEqual(events, [])

    def test_build_timeline_sorting(self) -> None:
        """Verify that built timeline events are sorted chronologically."""
        # Querying an existing case from seed database
        events = build_timeline("FIR-7001")
        self.assertTrue(len(events) > 0)
        
        # Check chronological ordering
        for i in range(len(events) - 1):
            t1 = events[i].timestamp
            t2 = events[i + 1].timestamp
            self.assertTrue(t1 <= t2, f"Events are not in chronological order: {t1} > {t2}")


class TestTimelineAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.app = app
        # Override authentication check for tests
        app.dependency_overrides[require_roles("analyst", "supervisor", "admin")] = lambda: {"username": "test-user", "role": "analyst"}

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_get_timeline_success(self) -> None:
        """Verify timeline GET endpoint returns 200 and matches Pydantic Response model."""
        response = self.client.get("/api/cases/FIR-7001/timeline")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["case_id"], "FIR-7001")
        self.assertIn("events", data)
        self.assertIsInstance(data["events"], list)
        
        # Verify schema field constraints
        for event in data["events"]:
            self.assertIn("event_id", event)
            self.assertIn("timestamp", event)
            self.assertIn("source_system", event)
            self.assertIn("event_type", event)
            self.assertIn("title", event)
            self.assertIn("description", event)
            self.assertIn("confidence", event)
            self.assertIn("severity", event)

    def test_get_timeline_not_found(self) -> None:
        """Verify querying timeline for unknown case returns 404."""
        response = self.client.get("/api/cases/invalid-case-id/timeline")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Case not found")

    def test_get_timeline_dependency_injection(self) -> None:
        """Verify timeline service dependency injection and override capability."""
        from backend.app.api.timeline import get_timeline_service
        
        mock_payload = {
            "case_id": "FIR-7001",
            "events": [
                {
                    "event_id": "EVT-MOCK1",
                    "timestamp": "2026-07-26T06:00:00Z",
                    "source_system": "Mock System",
                    "event_type": "Mock Event",
                    "title": "Mock Title",
                    "description": "Mock Description",
                    "confidence": 0.99,
                    "linked_case": "FIR-7001",
                    "resolved_entities": ["Mock Person"],
                    "supporting_evidence": ["Mock Doc"],
                    "severity": "LOW"
                }
            ]
        }
        
        self.app.dependency_overrides[get_timeline_service] = lambda: lambda case_id: mock_payload
        
        response = self.client.get("/api/cases/FIR-7001/timeline")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["events"]), 1)
        self.assertEqual(data["events"][0]["source_system"], "Mock System")
        self.assertEqual(data["events"][0]["severity"], "LOW")


if __name__ == "__main__":
    unittest.main()

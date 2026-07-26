"""Unit and integration tests for the Morning Intelligence Brief."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import require_roles
from backend.app.services.brief.aggregator import aggregate_intelligence_data
from backend.app.services.brief.metrics import calculate_executive_metrics
from backend.app.services.brief.templates import render_brief_narrative
from backend.app.services.brief.cache import clear_brief_cache


class TestBriefAggregatorAndMetrics(unittest.TestCase):
    def test_aggregation_fields(self) -> None:
        data = aggregate_intelligence_data()
        self.assertIn("highest_risk_score", data)
        self.assertIn("new_hotspots_count", data)
        self.assertIn("incident_growth_rate", data)

    def test_metrics_calculations(self) -> None:
        agg = {
            "highest_risk_score": 80,
            "new_hotspots_count": 2,
            "incident_growth_rate": 15.0,
            "network_connected_cases": 4,
            "recommendations_count": 5
        }
        res = calculate_executive_metrics(agg)
        self.assertTrue(res["overall_threat_score"] > 50)
        self.assertEqual(res["risk_trend"], "INCREASING")


class TestBriefAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.app = app
        app.dependency_overrides[require_roles("analyst", "supervisor", "admin")] = lambda: {"username": "test-user", "role": "analyst"}
        app.dependency_overrides[require_roles("supervisor", "admin")] = lambda: {"username": "test-supervisor", "role": "supervisor"}
        clear_brief_cache()

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_get_morning_brief(self) -> None:
        response = self.client.get("/api/intelligence/brief")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("threat_level", data)
        self.assertIn("summary", data)

    def test_export_morning_brief_markdown(self) -> None:
        response = self.client.get("/api/intelligence/brief/export?format=markdown")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Executive Crime Intelligence Brief", response.content)


if __name__ == "__main__":
    unittest.main()

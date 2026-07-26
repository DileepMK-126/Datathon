"""Unit and integration tests for the Patrol Recommendation Engine."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import require_roles
from backend.app.services.recommendations.rules import evaluate_patrol_rules
from backend.app.services.recommendations.priority import determine_recommendation_priority
from backend.app.services.recommendations.scheduler import schedule_patrol_interval
from backend.app.services.recommendations.engine import generate_zone_recommendations
from backend.app.services.recommendations.cache import clear_recommendations_cache


class TestPatrolRules(unittest.TestCase):
    def test_night_patrol_rule_match(self) -> None:
        # Risk > 70, night share > 0.55
        matches = evaluate_patrol_rules(risk_score=75, has_hotspot=True, night_share=0.65, patrol_gap=0.3)
        categories = {m["category"] for m in matches}
        self.assertIn("Increase night patrol", categories)

    def test_patrol_frequency_match(self) -> None:
        # Gap > 0.40
        matches = evaluate_patrol_rules(risk_score=40, has_hotspot=False, night_share=0.2, patrol_gap=0.5)
        categories = {m["category"] for m in matches}
        self.assertIn("Increase patrol frequency", categories)


class TestPatrolPriority(unittest.TestCase):
    def test_priority_critical(self) -> None:
        res = determine_recommendation_priority(risk_score=85, has_hotspot=True)
        self.assertEqual(res["priority"], "Critical")
        self.assertEqual(res["confidence"], 95)


class TestPatrolRecommendationsAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.app = app
        app.dependency_overrides[require_roles("analyst", "supervisor", "admin")] = lambda: {"username": "test-user", "role": "analyst"}
        app.dependency_overrides[require_roles("supervisor", "admin")] = lambda: {"username": "test-supervisor", "role": "supervisor"}
        clear_recommendations_cache()

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_get_recommendations_for_zone(self) -> None:
        response = self.client.get("/api/recommendations/sector-7")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["zone_id"], "sector-7")
        self.assertTrue(len(data["recommendations"]) > 0)

    def test_approve_recommendation(self) -> None:
        response = self.client.post("/api/recommendations/rec-sector-7-1/approve")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["recommendation_id"], "rec-sector-7-1")
        self.assertTrue(data["approved"])


if __name__ == "__main__":
    unittest.main()

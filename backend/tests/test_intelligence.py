"""Unit tests for the Intelligence Engine, templates, rules, and mock API outputs."""

from __future__ import annotations

import unittest
from backend.app.services.intelligence.rules import evaluate_priority, calculate_confidence
from backend.app.services.intelligence.templates import get_hotspot_text, get_trend_text
from backend.app.services.intelligence.engine import generate_zone_intelligence


class TestIntelligenceRules(unittest.TestCase):
    def test_evaluate_priority_critical(self) -> None:
        """Verify priority evaluates to CRITICAL for high risk and anomalies."""
        res = evaluate_priority(risk_score=85, anomaly_detected=True, cluster_size=6)
        self.assertEqual(res, "CRITICAL")

    def test_evaluate_priority_high(self) -> None:
        """Verify priority evaluates to HIGH for elevated parameters."""
        res = evaluate_priority(risk_score=76, anomaly_detected=False, cluster_size=5)
        self.assertEqual(res, "HIGH")

    def test_evaluate_priority_low(self) -> None:
        """Verify priority evaluates to LOW for guarded parameters."""
        res = evaluate_priority(risk_score=20, anomaly_detected=False, cluster_size=1)
        self.assertEqual(res, "LOW")

    def test_calculate_confidence_surge(self) -> None:
        """Verify calculate_confidence adds heuristic adjustments."""
        res = calculate_confidence(base_confidence=60, anomaly_detected=True, linked_cases_count=3, hotspot_change=60)
        # 60 (base) + 8 (anomaly) + 10 (linked cases) + 5 (surge) = 83
        self.assertEqual(res, 83)


class TestIntelligenceTemplates(unittest.TestCase):
    def test_hotspot_text(self) -> None:
        """Verify hotspot summary compiles with correct parameters."""
        text = get_hotspot_text("Sector 7", "burglary", 5, 24)
        self.assertIn("Sector 7", text)
        self.assertIn("5 active incidents", text)
        self.assertIn("24% deviation", text)

    def test_trend_text_anomaly(self) -> None:
        """Verify anomaly volume text is formatted correctly."""
        text = get_trend_text(anomaly_detected=True, baseline=12.4, period_days=28)
        self.assertIn("Isolation Forest", text)
        self.assertIn("12.4", text)


class TestIntelligenceEngine(unittest.TestCase):
    def test_engine_fallback(self) -> None:
        """Verify that the engine falls back gracefully for unknown zones."""
        res = generate_zone_intelligence("unknown-zone-id")
        self.assertEqual(res["priority"], "LOW")
        self.assertEqual(res["zone_id"], "unknown-zone-id")
        self.assertEqual(res["review_required"], True)


class TestIntelligenceAPI(unittest.TestCase):
    def setUp(self) -> None:
        from fastapi.testclient import TestClient
        from backend.app.main import app
        from backend.app.core.security import require_roles
        
        self.client = TestClient(app)
        self.app = app
        # Override authentication check for tests
        app.dependency_overrides[require_roles("analyst", "supervisor", "admin")] = lambda: {"username": "test-user", "role": "analyst"}

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_get_intelligence_success(self) -> None:
        """Verify requesting intelligence for an existing zone returns 200 and fits the response model."""
        response = self.client.get("/api/intelligence?zone_id=sector-7")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["zone_id"], "sector-7")
        self.assertEqual(data["zone_name"], "Sector 7")
        self.assertIn("priority", data)
        self.assertIn("confidence", data)
        self.assertIn("summary", data)
        self.assertIsInstance(data["drivers"], list)
        self.assertIsInstance(data["evidence"], list)
        self.assertIsInstance(data["recommendations"], list)
        self.assertEqual(data["review_required"], True)

    def test_get_intelligence_not_found(self) -> None:
        """Verify requesting intelligence for an unknown zone returns 404."""
        response = self.client.get("/api/intelligence?zone_id=invalid-zone-id")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Unknown zone")

    def test_get_intelligence_dependency_injection(self) -> None:
        """Verify that the intelligence generator service is injected and can be overridden."""
        from backend.app.api.intelligence import get_intelligence_service
        
        mock_payload = {
            "zone_id": "sector-7",
            "zone_name": "Mocked Zone",
            "priority": "CRITICAL",
            "confidence": 99,
            "summary": "This is a mock summary.",
            "drivers": ["Mock Driver"],
            "evidence": ["Mock Evidence"],
            "recommendations": ["Mock Recommendation"],
            "review_required": False
        }
        
        self.app.dependency_overrides[get_intelligence_service] = lambda: lambda zone_id: mock_payload
        
        response = self.client.get("/api/intelligence?zone_id=sector-7")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["zone_name"], "Mocked Zone")
        self.assertEqual(data["priority"], "CRITICAL")
        self.assertEqual(data["review_required"], False)


if __name__ == "__main__":
    unittest.main()


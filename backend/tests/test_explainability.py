"""Unit and integration tests for the Explainable AI (XAI) risk prediction module."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import require_roles
from backend.app.services.explainability.shap_engine import calculate_exact_shap
from backend.app.services.explainability.confidence import evaluate_confidence
from backend.app.services.explainability.engine import get_risk_explanation
from backend.app.services.explainability.cache import get_cached_explanation, clear_explainability_cache


class TestSHAPEngine(unittest.TestCase):
    def test_calculate_exact_shap(self) -> None:
        # Vector corresponding to zone features: volume, burglary, night, linked, patrol gap
        test_vector = [2.0, 0.40, 0.60, 0.33, 0.50]
        attributions = calculate_exact_shap(test_vector)
        
        self.assertEqual(len(attributions), 5)
        self.assertIn("Recent incident volume", attributions)
        self.assertIn("Burglary concentration", attributions)
        self.assertIn("Night-time activity", attributions)
        self.assertIn("Linked-case density", attributions)
        self.assertIn("Patrol coverage gap", attributions)
        
        # Attributions should be float values representing contribution impact
        for name, value in attributions.items():
            self.assertIsInstance(value, float)


class TestConfidence(unittest.TestCase):
    def test_confidence_calculations(self) -> None:
        c1 = evaluate_confidence(0.95)
        self.assertEqual(c1["level"], "Very High")
        self.assertTrue(c1["score"] >= 80)

        c2 = evaluate_confidence(0.50)
        self.assertEqual(c2["level"], "Medium")
        self.assertTrue(c2["score"] < 70)


class TestExplainabilityEngine(unittest.TestCase):
    def setUp(self) -> None:
        clear_explainability_cache()

    def test_get_risk_explanation_success(self) -> None:
        res = get_risk_explanation("sector-7")
        self.assertIsNotNone(res)
        self.assertEqual(res["zone_id"], "sector-7")
        self.assertIn("risk", res)
        self.assertIn("confidence", res)
        self.assertIn("positive_contributors", res)
        self.assertIn("negative_contributors", res)
        self.assertIn("summary", res)

    def test_get_risk_explanation_not_found(self) -> None:
        res = get_risk_explanation("invalid-zone-id")
        self.assertIsNone(res)


class TestExplainabilityAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.app = app
        app.dependency_overrides[require_roles("analyst", "supervisor", "admin")] = lambda: {"username": "test-user", "role": "analyst"}

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_explain_api_endpoint_success(self) -> None:
        response = self.client.get("/api/risks/explain/sector-7")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["zone_id"], "sector-7")
        self.assertIn("risk", data)
        self.assertIn("confidence", data)
        self.assertIn("positive_contributors", data)


if __name__ == "__main__":
    unittest.main()

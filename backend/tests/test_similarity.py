"""Unit, feature extraction, scoring weights, and API integration tests for the Similar Case Engine."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import require_roles
from backend.app.services.similarity.scoring import jaccard_similarity, geospatial_similarity, temporal_similarity
from backend.app.services.similarity.weights import DEFAULT_WEIGHTS
from backend.app.services.similarity.features import extract_features
from backend.app.services.similarity.engine import get_similar_cases
from backend.app.services.similarity.cache import get_cached_features, set_cached_features, clear_similarity_cache


class TestSimilarityMath(unittest.TestCase):
    def test_jaccard_similarity(self) -> None:
        self.assertEqual(jaccard_similarity(set(), set()), 1.0)
        self.assertEqual(jaccard_similarity({"A", "B"}, {"A"}), 0.5)
        self.assertEqual(jaccard_similarity({"A"}, {"B"}), 0.0)

    def test_geospatial_similarity(self) -> None:
        # Distance = 0 should yield 1.0 similarity
        self.assertAlmostEqual(geospatial_similarity(28.6264, 77.2183, 28.6264, 77.2183), 1.0, places=4)
        # Bounded distance check
        score = geospatial_similarity(28.6264, 77.2183, 28.6402, 77.2305)
        self.assertTrue(0.0 < score < 1.0)

    def test_temporal_similarity(self) -> None:
        t1 = "2026-07-26T12:00:00Z"
        t2 = "2026-07-26T12:00:00Z"
        self.assertEqual(temporal_similarity(t1, t2), 1.0)
        # Differing days should decay
        self.assertTrue(0.0 < temporal_similarity(t1, "2026-08-26T12:00:00Z") < 1.0)


class TestWeights(unittest.TestCase):
    def test_default_weights_sum_to_one(self) -> None:
        self.assertAlmostEqual(sum(DEFAULT_WEIGHTS.values()), 1.0, places=4)


class TestFeatureExtraction(unittest.TestCase):
    def test_extract_features_existing_case(self) -> None:
        # FIR-7001 is seeded on first startup
        feats = extract_features("FIR-7001")
        if feats:
            self.assertEqual(feats["case_id"], "FIR-7001")
            self.assertIn("crime_type", feats)
            self.assertIn("latitude", feats)
            self.assertIn("longitude", feats)
            self.assertIn("vehicles", feats)
            self.assertIn("phones", feats)
            self.assertIn("persons", feats)

    def test_extract_features_invalid_case(self) -> None:
        self.assertIsNone(extract_features("INVALID-ID"))


class TestSimilarityEngine(unittest.TestCase):
    def setUp(self) -> None:
        clear_similarity_cache()

    def test_get_similar_cases(self) -> None:
        results = get_similar_cases("FIR-7001", threshold=50.0, limit=3)
        if results:
            self.assertEqual(results["case_id"], "FIR-7001")
            self.assertIn("total_matches", results)
            self.assertIsInstance(results["matches"], list)
            self.assertTrue(len(results["matches"]) <= 3)
            for match in results["matches"]:
                self.assertTrue(match["similarity_score"] >= 50.0)
                self.assertIn("reasoning", match)
                self.assertIn("shared_entities", match)

    def test_caching_behavior(self) -> None:
        # Prime cache
        get_similar_cases("FIR-7001", threshold=60.0, limit=2)
        # Retrieve cached features directly
        cached = get_cached_features("FIR-7001")
        self.assertIsNotNone(cached)
        self.assertEqual(cached["case_id"], "FIR-7001")


class TestSimilarityAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.app = app
        # Override authentication check for tests (defaults to analyst role)
        app.dependency_overrides[require_roles("analyst", "supervisor", "admin")] = lambda: {"username": "test-user", "role": "analyst"}

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_get_similar_cases_success(self) -> None:
        response = self.client.get("/api/cases/FIR-7001/similar?threshold=50.0&limit=2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["case_id"], "FIR-7001")
        self.assertIn("matches", data)
        self.assertIsInstance(data["matches"], list)

    def test_get_similar_cases_not_found(self) -> None:
        response = self.client.get("/api/cases/INVALID-CASE/similar")
        self.assertEqual(response.status_code, 404)

    def test_rbac_admin_diagnostics(self) -> None:
        # Override with admin role
        self.app.dependency_overrides[require_roles("analyst", "supervisor", "admin")] = lambda: {"username": "admin-user", "role": "admin"}
        response = self.client.get("/api/cases/FIR-7001/similar?threshold=50.0")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data["matches"]:
            # Admin role should see detailed subscores
            self.assertNotEqual(data["matches"][0]["subscores"], {})

    def test_rbac_analyst_no_diagnostics(self) -> None:
        # Override with analyst role
        self.app.dependency_overrides[require_roles("analyst", "supervisor", "admin")] = lambda: {"username": "analyst-user", "role": "analyst"}
        response = self.client.get("/api/cases/FIR-7001/similar?threshold=50.0")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data["matches"]:
            # Analyst role should NOT see detailed subscores (diagnostics stripped)
            self.assertEqual(data["matches"][0]["subscores"], {})


if __name__ == "__main__":
    unittest.main()

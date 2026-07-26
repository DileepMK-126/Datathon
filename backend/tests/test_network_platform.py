"""Unit and integration tests for the Criminal Network Intelligence Platform."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import require_roles
from backend.app.services.network.graph_engine import build_full_network_graph
from backend.app.services.network.pathfinder import find_shortest_path_explanation
from backend.app.services.network.export import export_graph_to_json, export_graph_to_graphml
from backend.app.services.network.cache import clear_network_cache


class TestGraphEngine(unittest.TestCase):
    def setUp(self) -> None:
        clear_network_cache()

    def test_build_full_graph(self) -> None:
        G = build_full_network_graph()
        self.assertIsNotNone(G)
        self.assertTrue(len(G) > 0)
        
        # Test node attributes
        for node, attrs in G.nodes(data=True):
            self.assertIn("kind", attrs)
            self.assertIn("label", attrs)
            self.assertIn("centrality", attrs)
            self.assertIn("community", attrs)


class TestPathfinder(unittest.TestCase):
    def test_shortest_path_no_path(self) -> None:
        G = build_full_network_graph()
        # Find path between two non-existent nodes
        res = find_shortest_path_explanation(G, "person:invalid-x", "person:invalid-y")
        self.assertIsNone(res)


class TestNetworkAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.app = app
        app.dependency_overrides[require_roles("analyst", "supervisor", "admin")] = lambda: {"username": "test-user", "role": "analyst"}
        app.dependency_overrides[require_roles("supervisor", "admin")] = lambda: {"username": "test-supervisor", "role": "supervisor"}

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_get_network_graph(self) -> None:
        response = self.client.get("/api/network")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("nodes", data)
        self.assertIn("links", data)
        self.assertIn("layout", data)

    def test_get_centrality(self) -> None:
        response = self.client.get("/api/network/centrality?limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) <= 5)

    def test_get_community(self) -> None:
        response = self.client.get("/api/network/community")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) > 0)

    def test_get_repeat_offenders(self) -> None:
        response = self.client.get("/api/network/repeat-offenders")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_export_network_graph(self) -> None:
        response = self.client.get("/api/network/export?format=graphml")
        self.assertEqual(response.status_code, 200)
        self.assertIn("graphml", response.text)


if __name__ == "__main__":
    unittest.main()

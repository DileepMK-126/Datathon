"""Referential integrity and volume verification tests for the synthetic dataset."""

from __future__ import annotations

import unittest
from backend.app.db.connection import connection
from backend.app.db.seeder import initialize_database


class TestDatasetIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        initialize_database()

    def test_database_record_volumes(self) -> None:
        """Verify the database has been seeded with high-volume synthetic profiles."""
        with connection() as conn:
            # 1. Check cases
            cases_count = conn.execute("SELECT COUNT(*) AS count FROM cases").fetchone()["count"]
            self.assertGreaterEqual(cases_count, 3000)

            # 2. Check incidents (5 per case -> 15,000 incidents)
            incidents_count = conn.execute("SELECT COUNT(*) AS count FROM incidents").fetchone()["count"]
            self.assertGreaterEqual(incidents_count, 15000)

            # 3. Check distinct entity names
            person_count = conn.execute(
                "SELECT COUNT(DISTINCT normalized_value) AS count FROM case_entities WHERE entity_type = 'person'"
            ).fetchone()["count"]
            self.assertGreaterEqual(person_count, 1800)

    def test_no_orphan_records(self) -> None:
        """Verify that every incident has a valid corresponding case profile (foreign key check)."""
        with connection() as conn:
            orphans = conn.execute(
                "SELECT COUNT(*) AS count FROM incidents WHERE case_id NOT IN (SELECT id FROM cases)"
            ).fetchone()["count"]
            self.assertEqual(orphans, 0)
            
            orphan_entities = conn.execute(
                "SELECT COUNT(*) AS count FROM case_entities WHERE case_id NOT IN (SELECT id FROM cases)"
            ).fetchone()["count"]
            self.assertEqual(orphan_entities, 0)

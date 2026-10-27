"""Phase 0 tests must run with Python stdlib unittest without dependencies."""
import json
import unittest
from pathlib import Path
from nulltrace.doctor import check_project_manifest, inspect_environment

ROOT = Path(__file__).resolve().parents[1]

class Phase0Tests(unittest.TestCase):
    def test_mission_catalog_contains_100_unique_ids(self):
        missions = json.loads((ROOT / "content/missions/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(len(missions), 100)
        ids = [row["id"] for row in missions]
        self.assertEqual(len(set(ids)), 100)
        self.assertEqual(ids[0], "CH01-M01")
        self.assertEqual(ids[-1], "CH10-M10")
        for row in missions:
            self.assertIn("learning_objective", row)
            self.assertIn("verification", row)
            self.assertIn("mode", row)

    def test_project_manifest(self):
        self.assertEqual(check_project_manifest(ROOT), [])

    def test_environment_inspection_read_only(self):
        status = inspect_environment()
        self.assertIsInstance(status["python"], str)
        self.assertIn("pygame_available", status)

if __name__ == "__main__":
    unittest.main()

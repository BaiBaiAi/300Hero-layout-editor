import unittest

from app import hall_scene


class HallOnlyTests(unittest.TestCase):
    def test_hall_project_is_accepted(self):
        project = {"format": "300hero-layout/1", "nodes": []}
        self.assertIs(hall_scene(project), project)

    def test_arena_project_and_mode_are_rejected(self):
        for project in (
            {"format": "300arena-layout/1", "mode": "arena", "nodes": []},
            {"format": "300hero-layout/1", "mode": "arena", "nodes": []},
        ):
            with self.subTest(project=project), self.assertRaisesRegex(ValueError, "仅支持大厅布局"):
                hall_scene(project)


if __name__ == "__main__":
    unittest.main()

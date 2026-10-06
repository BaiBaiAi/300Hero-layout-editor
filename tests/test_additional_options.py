import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import additional_options as options


class AdditionalOptionsTests(unittest.TestCase):
    def test_camera_target_only_contains_main_data_lua(self):
        self.assertEqual(
            options.TARGETS["camera_35"],
            [(r"..\data\script\gamehall\setup\setup_game.lua", "setup_game.lua")],
        )

    def test_disabled_option_without_baseline_does_not_locate_target(self):
        scene = {"options": {"auto_accept_match": False, "camera_35": False,
                             "clickable_surrender": True}}
        with tempfile.TemporaryDirectory() as folder, patch.object(
                options, "_locate", side_effect=AssertionError("不应查找未启用的选项目标")):
            changes = options.build_option_changes(
                scene, [], Path(folder), Path(folder), create_baseline=False)
        self.assertEqual(changes, [])

    def test_removed_option_in_old_project_is_ignored(self):
        self.assertNotIn("clickable_surrender", options.normalized_options(
            {"options": {"clickable_surrender": True}}))

    def test_enabled_camera_uses_main_data_target(self):
        scene = {"options": {"camera_35": True}}
        entry = SimpleNamespace(path=options.TARGETS["camera_35"][0][0])
        pack = SimpleNamespace(entries=[entry])
        current = b"old"
        desired = b"new"

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "templates").mkdir()
            (root / "templates" / "setup_game.lua").write_bytes(desired)
            with patch.object(options.jc, "read_entry", return_value=current):
                changes = options.build_option_changes(
                    scene, [pack], root / "templates", root / "baselines", False)

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["path"], r"..\data\script\gamehall\setup\setup_game.lua")
        self.assertEqual(changes[0]["raw"], desired)


if __name__ == "__main__":
    unittest.main()

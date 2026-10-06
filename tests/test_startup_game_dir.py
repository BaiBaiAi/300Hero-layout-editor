import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import app
from settings_store import choose_game_dir, has_jmp_files, load_settings, save_settings


class StartupGameDirTests(unittest.TestCase):
    def test_invalid_saved_dir_prompts_and_remembers_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            game_dir = root / "game"
            game_dir.mkdir()
            (game_dir / "Data12.jmp").write_bytes(b"")
            settings_file = root / "settings.json"
            save_settings(settings_file, {"gameDir": str(root / "old")})
            server = Mock(server_port=8123)
            with (patch.object(app, "SETTINGS_FILE", settings_file),
                  patch.object(app, "choose_game_dir", return_value=str(game_dir)) as chooser,
                  patch.object(app, "ThreadingHTTPServer", return_value=server),
                  patch.object(sys, "argv", ["app.py", "--no-browser"])):
                self.assertEqual(app.main(), 0)
                chooser.assert_called_once_with(str(root / "old"))
                self.assertEqual(load_settings(settings_file)["gameDir"], str(game_dir))

                chooser.reset_mock()
                self.assertEqual(app.main(), 0)
                chooser.assert_not_called()

            (game_dir / "Data12.jmp").unlink()
            with (patch.object(app, "SETTINGS_FILE", settings_file),
                  patch.object(app, "choose_game_dir", return_value="") as chooser,
                  patch.object(sys, "argv", ["app.py", "--no-browser"])):
                self.assertEqual(app.main(), 1)
                chooser.assert_called_once_with(str(game_dir))

    def test_empty_dir_is_never_valid(self):
        self.assertFalse(has_jmp_files(""))
        self.assertFalse(has_jmp_files(None))

    def test_picker_explains_invalid_choice_and_asks_again(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            game_dir = root / "game"
            game_dir.mkdir()
            (game_dir / "Data5.jmp").write_bytes(b"")
            window = Mock()
            dialog = Mock()
            dialog.askdirectory.side_effect = [str(root), str(game_dir)]
            messagebox = Mock()
            tkinter = SimpleNamespace(Tk=Mock(return_value=window),
                                      filedialog=dialog, messagebox=messagebox)
            with patch.dict(sys.modules, {"tkinter": tkinter}):
                self.assertEqual(choose_game_dir(), str(game_dir))
            self.assertEqual(dialog.askdirectory.call_count, 2)
            messagebox.showerror.assert_called_once()
            window.destroy.assert_called_once()


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path


def load_settings(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def save_settings(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def has_jmp_files(game_dir: str) -> bool:
    if not isinstance(game_dir, str) or not game_dir.strip():
        return False
    folder = Path(game_dir)
    return folder.is_dir() and any(path.is_file() for path in folder.glob("Data*.jmp"))


def choose_game_dir(initial: str = "") -> str:
    root = None
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        while True:
            selected = filedialog.askdirectory(
                title="请选择包含 Data*.jmp 的 300英雄游戏目录",
                initialdir=initial if isinstance(initial, str) and Path(initial).is_dir() else None,
                mustexist=True,
                parent=root,
            )
            if not selected:
                return ""
            if has_jmp_files(selected):
                return selected
            messagebox.showerror("游戏目录无效", "所选目录中没有 Data*.jmp，请选择 300英雄游戏目录。", parent=root)
            initial = selected
    except Exception:
        return ""
    finally:
        if root is not None:
            root.destroy()

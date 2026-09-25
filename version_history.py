from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import jmp_core as jc


def _safe_name(value: str) -> str:
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in value)


def snapshot_current_version(patches, packs: list[jc.Pack], root: Path, game_dir: str) -> Path:
    """Extract every target's current raw data before each apply operation."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    game_tag = hashlib.sha256(str(Path(game_dir).resolve()).encode("utf-8")).hexdigest()[:12]
    folder = root / game_tag / stamp
    files = folder / "files"
    files.mkdir(parents=True, exist_ok=False)
    manifest = {"format": "300hero-previous-version/1", "createdAt": datetime.now().isoformat(),
                "gameDir": str(Path(game_dir).resolve()), "entries": []}
    by_path = {(e.path.replace('/', '\\').lower()): (pack, e)
               for pack in packs for e in pack.entries}
    for patch in patches:
        pair = by_path.get(patch.internal_path.replace('/', '\\').lower())
        if pair is None:
            continue
        pack, entry = pair
        raw = jc.read_entry(pack, entry)
        filename = "%s_%05d_%s" % (pack.base_name(), entry.index, _safe_name(Path(entry.path).name))
        output = files / filename
        output.write_bytes(raw)
        manifest["entries"].append({"pack": pack.base_name(), "packPath": pack.file,
                                    "index": entry.index, "internalPath": entry.path,
                                    "file": str(output.relative_to(folder)).replace('\\', '/'),
                                    "size": len(raw), "md5": hashlib.md5(raw).hexdigest(),
                                    "sha256": hashlib.sha256(raw).hexdigest()})
    (folder / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return folder

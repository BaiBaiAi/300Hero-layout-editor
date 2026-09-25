from __future__ import annotations

import base64
import difflib
import hashlib
import json
from pathlib import Path

import jmp_core as jc


TARGETS = {
    "auto_accept_match": [("..\\data\\script\\gamehall\\wait\\matchready.lua", "matchready.lua")],
    "camera_35": [
        ("..\\data\\script\\gamehall\\setup\\setup_game.lua", "setup_game.lua"),
        ("..\\pve\\data\\script\\gamehall\\setup\\setup_game.lua", "setup_game_pve.lua"),
        ("..\\tiyan\\data\\script\\gamehall\\setup\\setup_game.lua", "setup_game_tiyan.lua"),
    ],
    "clickable_surrender": [("..\\data\\script\\gamehall\\setup\\setup.lua", "setup.lua")],
}


def defaults():
    return {"auto_minimize_chat": True, "auto_accept_match": False,
            "camera_35": False, "clickable_surrender": False}


def normalized_options(scene: dict):
    result = defaults()
    result.update({k: bool(v) for k, v in (scene.get("options") or {}).items() if k in result})
    return result


def _locate(packs, internal_path):
    target = internal_path.replace("/", "\\").lower()
    for pack in packs:
        for entry in pack.entries:
            if entry.path.replace("/", "\\").lower() == target:
                return pack, entry
    raise FileNotFoundError("未找到附加选项目标：" + internal_path)


def _baseline_file(folder: Path, internal_path: str):
    key = hashlib.sha256(internal_path.lower().encode()).hexdigest()[:16]
    return folder / (key + ".json")


def _read_baseline(folder: Path, packs, internal_path: str, create: bool):
    path = _baseline_file(folder, internal_path)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return base64.b64decode(data["data"])
    pack, entry = _locate(packs, internal_path)
    raw = jc.read_entry(pack, entry)
    if create:
        folder.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"path": internal_path, "pack": pack.base_name(), "index": entry.index,
                                    "sha256": hashlib.sha256(raw).hexdigest(),
                                    "data": base64.b64encode(raw).decode("ascii")}, ensure_ascii=False, indent=2), encoding="utf-8")
    return raw


def build_option_changes(scene: dict, packs, template_dir: Path, baseline_dir: Path, create_baseline=False):
    opts = normalized_options(scene)
    changes = []
    for option, targets in TARGETS.items():
        for internal_path, template_name in targets:
            pack, entry = _locate(packs, internal_path)
            current = jc.read_entry(pack, entry)
            baseline_path = _baseline_file(baseline_dir, internal_path)
            if opts[option]:
                baseline = _read_baseline(baseline_dir, packs, internal_path, create_baseline)
                desired = (template_dir / template_name).read_bytes()
            elif baseline_path.exists():
                baseline = _read_baseline(baseline_dir, packs, internal_path, False)
                desired = baseline
            else:
                continue
            if current != desired:
                a = current.decode("gb18030", errors="replace").splitlines(True)
                b = desired.decode("gb18030", errors="replace").splitlines(True)
                diff = "".join(difflib.unified_diff(a, b, fromfile=internal_path + " (当前)",
                                                     tofile=internal_path + " (附加选项)"))
                changes.append({"option": option, "path": internal_path, "pack": pack, "entry": entry,
                                "raw": desired, "diff": diff})
    return changes


def preview_options(scene, packs, template_dir, baseline_dir):
    return [{"option": x["option"], "path": x["path"], "pack": x["pack"].base_name(), "diff": x["diff"]}
            for x in build_option_changes(scene, packs, template_dir, baseline_dir, False)]


def apply_options(scene, packs, template_dir, baseline_dir, backup_dir):
    changes = build_option_changes(scene, packs, template_dir, baseline_dir, True)
    results = []
    for change in changes:
        result = jc.patch_entry(change["pack"], change["entry"], change["raw"], str(backup_dir), allow_overflow=True)
        if jc.read_entry(change["pack"], change["entry"]) != change["raw"]:
            raise IOError("附加选项写入校验失败：" + change["path"])
        results.append(result)
    return results


def export_options(scene, packs, template_dir, baseline_dir, folder: Path):
    changes = build_option_changes(scene, packs, template_dir, baseline_dir, False)
    if not changes:
        return []
    target = folder / "additional_options"
    target.mkdir(parents=True, exist_ok=True)
    manifest, diffs = [], []
    for index, change in enumerate(changes, 1):
        name = "%02d_%s_%s" % (index, change["option"], Path(change["path"]).name)
        (target / name).write_bytes(change["raw"])
        diffs.append(change["diff"])
        manifest.append({"option": change["option"], "internalPath": change["path"],
                         "pack": change["pack"].base_name(), "file": name,
                         "sha256": hashlib.sha256(change["raw"]).hexdigest()})
    (target / "additional_options.diff").write_text("\n".join(diffs), encoding="utf-8")
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest

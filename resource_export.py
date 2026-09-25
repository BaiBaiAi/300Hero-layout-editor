from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path, PureWindowsPath

from PIL import Image

import jmp_core as jc
from hall_scene import LuaSource


RESOURCE_EXTENSIONS = {
    ".png", ".bmp", ".dds", ".tga", ".jpg", ".jpeg", ".gif",
    ".x", ".moc", ".mtn", ".json", ".model", ".lua",
}

# These directories are the dynamic families used by the lobby. Some filenames are
# built at runtime from IDs and therefore cannot be discovered from string literals.
LOBBY_PREFIXES = (
    "..\\data\\ux\\main\\",
    "..\\data\\ux\\play\\",
    "..\\data\\uinew\\main\\expend\\",
    "..\\data\\uinew\\main\\chat\\",
    "..\\data\\uinew\\activity\\timetower\\",
    "..\\data\\magic\\common\\ui\\changwai\\datingjiemiananniu\\",
    "..\\ui\\icon\\skin\\320\\",
)

LOBBY_PATH_WORDS = (
    "\\live2d\\", "\\fastenter\\", "home-pop", "home-mask", "entrance",
)


def _safe_relative(internal_path: str) -> Path:
    value = internal_path.replace("/", "\\")
    while value.startswith("..\\"):
        value = value[3:]
    parts = []
    for part in PureWindowsPath(value).parts:
        if part in ("", ".", "..", "\\"):
            continue
        part = re.sub(r'[<>:"/\\|?*]', "_", part)
        parts.append(part)
    if not parts:
        raise ValueError("无效内部路径：" + internal_path)
    return Path(*parts)


def literal_resource_names(sources: dict[str, LuaSource]) -> set[str]:
    names = set()
    string_re = re.compile(r"(['\"])(.*?)(?<!\\)\1")
    for source in sources.values():
        for match in string_re.finditer(source.text):
            value = match.group(2).replace("/", "\\")
            # Keep both direct filenames and paths. Runtime expressions such as
            # 'btn'..key..'-01.png' are covered by the dynamic directory families.
            suffix = Path(value).suffix.lower()
            if suffix in RESOURCE_EXTENSIONS:
                names.add(value.lower())
                names.add(PureWindowsPath(value).name.lower())
    return names


def select_lobby_entries(packs: list[jc.Pack], sources: dict[str, LuaSource]):
    literals = literal_resource_names(sources)
    selected = {}
    for pack in packs:
        if not pack.parse_ok:
            continue
        for entry in pack.entries:
            path = entry.path.replace("/", "\\")
            low = path.lower()
            name = PureWindowsPath(path).name.lower()
            ext = PureWindowsPath(path).suffix.lower()
            if ext not in RESOURCE_EXTENSIONS:
                continue
            wanted = (
                any(low.startswith(prefix) for prefix in LOBBY_PREFIXES)
                or any(word in low for word in LOBBY_PATH_WORDS)
                or low in literals or name in literals
            )
            if not wanted:
                continue
            # The same internal path can occur in a mirror pack. Keep normal client
            # data first, then the first validated occurrence.
            score = ("\\pve\\" in low or "\\tiyan\\" in low, pack.base_name().lower())
            old = selected.get(low)
            if old is None or score < old[0]:
                selected[low] = (score, pack, entry)
    return [(pack, entry) for _score, pack, entry in selected.values()]


def _preview(raw: bytes, ext: str) -> tuple[bytes, str] | None:
    ext = ext.lower()
    if ext in (".png", ".gif", ".jpg", ".jpeg"):
        return raw, ext
    if ext not in (".bmp", ".dds", ".tga"):
        return None
    try:
        image = Image.open(io.BytesIO(raw)).convert("RGBA")
        out = io.BytesIO()
        image.save(out, format="PNG")
        return out.getvalue(), ".png"
    except Exception:
        return None


def extract_lobby_resources(packs: list[jc.Pack], sources: dict[str, LuaSource], root: Path,
                            progress=None) -> dict:
    raw_root = root / "game"
    web_root = root / "web"
    raw_root.mkdir(parents=True, exist_ok=True)
    web_root.mkdir(parents=True, exist_ok=True)
    entries = select_lobby_entries(packs, sources)
    manifest = []
    total_bytes = 0
    preview_count = 0
    for number, (pack, entry) in enumerate(entries, 1):
        raw = jc.read_entry(pack, entry)
        rel = _safe_relative(entry.path)
        raw_path = raw_root / rel
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(raw)
        preview = _preview(raw, rel.suffix)
        preview_rel = None
        if preview:
            preview_raw, preview_ext = preview
            preview_rel = rel.with_suffix(preview_ext)
            preview_path = web_root / preview_rel
            preview_path.parent.mkdir(parents=True, exist_ok=True)
            preview_path.write_bytes(preview_raw)
            preview_count += 1
        total_bytes += len(raw)
        manifest.append({
            "internalPath": entry.path,
            "pack": pack.base_name(),
            "index": entry.index,
            "size": len(raw),
            "md5": hashlib.md5(raw).hexdigest(),
            "raw": rel.as_posix(),
            "preview": preview_rel.as_posix() if preview_rel else None,
        })
        if progress and (number == 1 or number % 50 == 0 or number == len(entries)):
            progress(number, len(entries), entry.path)
    result = {
        "format": "300hero-assets/1",
        "resourceCount": len(manifest),
        "previewCount": preview_count,
        "totalBytes": total_bytes,
        "resources": manifest,
    }
    (root / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def load_asset_manifest(root: Path) -> dict | None:
    path = root / "manifest.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

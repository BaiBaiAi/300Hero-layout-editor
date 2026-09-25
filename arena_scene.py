from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

import jmp_core as jc
from hall_scene import LuaSource, normalize, source_line


CANVAS = {"width": 1920, "height": 1080}
TARGET_LUA = {
    "battle.lua", "lolmain.lua", "fight_bag.lua", "fight_target.lua", "minimap.lua",
    "score.lua", "teamplayer.lua", "summonerskill.lua", "statusprogress.lua",
    "timeprogress.lua", "state.lua", "useitem.lua", "surrender.lua",
}


def find_arena_sources(packs: Iterable[jc.Pack]) -> dict[str, LuaSource]:
    found: dict[str, LuaSource] = {}
    priority = {f"data{i}.jmp": i for i in range(20)}
    for pack in packs:
        if not pack.parse_ok:
            continue
        for entry in pack.entries:
            low = normalize(entry.path)
            name = low.rsplit("\\", 1)[-1]
            if name not in TARGET_LUA or "\\data\\script\\fight\\" not in low:
                continue
            if "\\pve\\" in low or "\\tiyan\\" in low or "observer" in low:
                continue
            raw = jc.read_entry(pack, entry)
            text = None
            for encoding in ("gb18030", "utf-8-sig", "utf-8"):
                try:
                    text = raw.decode(encoding)
                    break
                except UnicodeDecodeError:
                    pass
            text = text if text is not None else raw.decode("latin1")
            item = LuaSource(entry.path, pack.base_name(), entry.index, text, hashlib.md5(raw).hexdigest())
            old = found.get(name)
            if old is None or priority.get(pack.base_name().lower(), 0) > priority.get(old.pack.lower(), 0):
                found[name] = item
    return found


def _node(sources, node_id, label, group, x, y, w, h, anchor, source, root, needle, color, note=""):
    src = sources.get(source)
    return {
        "id": node_id, "label": label, "group": group, "type": "panel",
        "x": x, "y": y, "width": w, "height": h, "anchor": anchor,
        "visible": True, "locked": False, "opacity": 1.0, "scale": 1.0,
        "color": color, "children": [], "state": "all", "assetHint": "",
        "runtimeRoot": root, "note": note,
        "source": {"internalPath": src.path if src else source, "pack": src.pack if src else "未找到",
                   "index": src.index if src else None, "line": source_line(src.text, needle) if src else None,
                   "needle": needle, "md5": src.md5 if src else None},
    }


def build_arena_scene(sources: dict[str, LuaSource], game_dir: str, pack_summary=None) -> dict:
    n = []
    add = lambda *a, **kw: n.append(_node(sources, *a, **kw))
    add("score", "顶部计分条与时间", "顶部", 225, 0, 1470, 60, "top-center", "score.lua", "n_score_ui", "n_score_ui = CreateWindow", "#4b80d8", "竞技场比分、队伍与计时；顶部居中")
    add("target", "目标信息", "顶部", 0, 0, 258, 107, "top-left", "fight_target.lua", "n_fighttarget_ui", "n_fighttarget_ui = CreateWindow", "#d75a62", "选中英雄/单位的头像、血蓝与装备")
    add("team", "左侧队友栏", "左侧", 0, 140, 100, 800, "left-middle", "teamplayer.lua", "n_teamplayer_ui", "n_teamplayer_ui = CreateWindow", "#30a77b", "队友头像、血量及展开区域")
    add("bag", "英雄头像/属性/装备", "底部", 1052, 953, 868, 127, "bottom-right", "fight_bag.lua", "n_fightbag_ui", "n_fightbag_ui = CreateWindow", "#ae6ed1", "原脚本按右下锚定；截图中的左下样式可能由内部子控件横向展开")
    add("skills", "技能栏与生命法力", "底部", 710, 954, 500, 126, "bottom-center", "lolmain.lua", "n_lolmain_ui", "n_lolmain_ui = CreateWindow", "#df9b39", "底部居中，包含技能、升级按钮、生命/法力/经验")
    add("state", "状态与 Buff 栏", "底部", 560, 946, 800, 134, "bottom-center", "state.lua", "n_state_ui", "n_state_ui = CreateWindow", "#8a77d8", "英雄状态与 Buff/Debuff 图标")
    add("timeprogress", "施法/进度条", "底部", 830, 880, 259, 26, "bottom-center", "timeprogress.lua", "n_TimeProgress_ui", "n_TimeProgress_ui = CreateWindow", "#e3c75b", "回城或持续施法进度")
    add("statusprogress", "状态进度提示", "底部", 760, 830, 400, 40, "bottom-center", "statusprogress.lua", "n_statusProgress_ui", "n_statusProgress_ui = CreateWindow", "#ce72a0")
    add("minimap", "小地图", "右下", 1660, 820, 260, 260, "bottom-right", "minimap.lua", "n_minimap_ui", "n_minimap_ui = CreateWindow", "#48a7b8", "右下锚定，换分辨率时保持距右/下边缘")
    add("summoner", "召唤师技能面板", "弹出面板", 1100, 650, 472, 333, "bottom-center", "summonerskill.lua", "n_summonerskill_ui", "n_summonerskill_ui = CreateWindow", "#bb7a49")
    add("useitem", "道具使用/远程商店", "右上", 1481, 120, 439, 315, "top-right", "useitem.lua", "n_useitem_ui", "n_useitem_ui = CreateWindow", "#658ac7", "截图右上道具快捷区与相关弹出面板")
    add("surrender", "投降投票窗口", "弹出面板", 1648, 540, 272, 182, "right-middle", "surrender.lua", "n_surrender_ui", "n_surrender_ui = CreateWindow", "#bc5656")
    return {
        "format": "300arena-layout/1", "mode": "arena", "gameDir": game_dir,
        "canvas": dict(CANVAS), "preview": {"width": 1280, "height": 800},
        "state": "all", "options": {}, "nodes": n,
        "sources": {k: {"path": v.path, "pack": v.pack, "index": v.index, "md5": v.md5} for k, v in sources.items()},
        "warnings": ["未找到：" + x for x in sorted(TARGET_LUA - set(sources))],
        "packSummary": pack_summary or [],
    }


def analyze_arena(packs, game_dir: str):
    sources = find_arena_sources(packs)
    summary = [{"name": p.base_name(), "count": len(p.entries), "ok": p.parse_ok,
                "error": p.error, "readOnly": p.read_only} for p in packs]
    return sources, build_arena_scene(sources, game_dir, summary)


def export_arena_project(scene, sources, folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "竞技场布局.arenalayout.json").write_text(
        json.dumps(scene, ensure_ascii=False, indent=2), encoding="utf-8")
    source_dir = folder / "原始Lua"
    source_dir.mkdir(exist_ok=True)
    for name, source in sources.items():
        (source_dir / name).write_text(source.text, encoding="utf-8")
    return folder

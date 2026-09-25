from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import jmp_core as jc


CANVAS = {"width": 1280, "height": 800}

TARGET_LUA = {
    "game_hall.lua",
    "game_expend.lua",
    "game_shop_hero_equip.lua",
    "chat.lua",
    "game_main.lua",
    "game_uxbutton.lua",
    "game_loginui.lua",
}


@dataclass
class LuaSource:
    path: str
    pack: str
    index: int
    text: str
    md5: str


def normalize(path: str) -> str:
    return path.replace("/", "\\").lower()


def source_line(text: str, needle: str) -> int | None:
    for number, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return number
    return None


def find_lua_sources(packs: Iterable[jc.Pack]) -> dict[str, LuaSource]:
    found: dict[str, LuaSource] = {}
    priority = {"data9.jmp": 9, "data8.jmp": 8, "data7.jmp": 7, "data6.jmp": 6}
    for pack in packs:
        if not pack.parse_ok:
            continue
        for entry in pack.entries:
            low = normalize(entry.path)
            name = low.rsplit("\\", 1)[-1]
            if name not in TARGET_LUA or "\\data\\script\\" not in low:
                continue
            # Do not select the PVE/experience-server mirrors for the normal client.
            if "\\pve\\" in low or "\\tiyan\\" in low:
                continue
            raw = jc.read_entry(pack, entry)
            text = None
            for encoding in ("gb18030", "utf-8-sig", "utf-8"):
                try:
                    text = raw.decode(encoding)
                    break
                except UnicodeDecodeError:
                    pass
            if text is None:
                text = raw.decode("latin1")
            item = LuaSource(entry.path, pack.base_name(), entry.index, text,
                             hashlib.md5(raw).hexdigest())
            previous = found.get(name)
            if previous is None or priority.get(pack.base_name().lower(), 0) > priority.get(previous.pack.lower(), 0):
                found[name] = item
    return found


def _node(node_id: str, label: str, group: str, x: int, y: int, w: int, h: int,
          color: str, source: str, needle: str, sources: dict[str, LuaSource],
          *, visible: bool = True, locked: bool = False, children: list[str] | None = None,
          note: str = "", state: str = "all", asset_hint: str = "") -> dict:
    src = sources.get(source)
    return {
        "id": node_id,
        "label": label,
        "group": group,
        "type": "group" if children else "panel",
        "x": x, "y": y, "width": w, "height": h,
        "visible": visible, "locked": locked,
        "opacity": 1.0, "scale": 1.0,
        "color": color, "children": children or [],
        "state": state,
        "note": note,
        "assetHint": asset_hint,
        "source": {
            "internalPath": src.path if src else source,
            "pack": src.pack if src else "未找到",
            "index": src.index if src else None,
            "line": source_line(src.text, needle) if src else None,
            "needle": needle,
            "md5": src.md5 if src else None,
        },
    }


def build_scene(sources: dict[str, LuaSource], game_dir: str) -> dict:
    n = []
    add = lambda *a, **kw: n.append(_node(*a, sources=sources, **kw))

    add("background", "大厅背景", "背景与人物", 0, 0, 1280, 800, "#20364f",
        "game_hall.lua", "MainHall_BK = wnd:AddImage", locked=True,
        note="背景、动态效果和 home-mask 应同步调整", asset_hint="320Skin")
    add("home_mask", "大厅暗色遮罩", "背景与人物", 0, 0, 1280, 800, "#111827",
        "game_hall.lua", "home-mask.png", locked=True,
        note="安全模式：保留原 local mask，仅在创建位置隐藏；控制左侧、右侧、聊天区和四周的统一暗角",
        asset_hint="home-mask.png")
    add("live2d", "Live2D 人物层", "背景与人物", 0, 0, 1280, 800, "#66d9ef",
        "game_hall.lua", "AddLive2DWnd", visible=True, state="live2d",
        note="网页原型显示模型占位范围；游戏内由 AddLive2DWnd 渲染")
    add("live2d_pop", "Live2D 对话气泡", "Live2D 附属", 566, 122, 255, 140, "#fff0c2",
        "game_hall.lua", "Live2D_Pop =", state="live2d")
    add("live2d_bubble", "Live2D 点击气泡", "Live2D 附属", 566, 250, 97, 71, "#ffd27a",
        "game_hall.lua", "Live2D_Bubble =", state="live2d")
    add("live2d_dialog", "Live2D 左下对话", "Live2D 附属", 51, 463, 250, 173, "#efe5d3",
        "game_hall.lua", "dlg_live2d.BK =", state="live2d")
    add("live2d_switch", "Live2D 开关", "Live2D 附属", 200, 720, 85, 80, "#da9cff",
        "game_hall.lua", "btn_live2d =", state="live2d", asset_hint="otaku_1.BMP")
    add("skin_switch", "超级皮肤切换", "Live2D 附属", 285, 733, 109, 67, "#bb7cff",
        "game_hall.lua", "btn_switchsuper =", state="live2d", asset_hint="maho.BMP")

    add("top_nav", "顶部导航栏", "顶部", 0, 0, 610, 72, "#334b78",
        "game_shop_hero_equip.lua", "nav-top-bg.png", note="含 8 个导航按钮和选中高亮", asset_hint="nav-top-bg.png")
    add("top_assets", "货币与系统按钮", "顶部", 810, 0, 470, 100, "#4c5e85",
        "game_shop_hero_equip.lua", "show_money =", note="金币、钻石、设置、公告、邮件、好友、头像、最小化和关闭")
    add("top_banner", "左上宣传横幅", "活动", 10, 53, 236, 112, "#5179a6",
        "game_expend.lua", "NewTower =", asset_hint="newtower.png")
    add("left_activity", "左侧竖向功能", "活动", 8, 157, 55, 422, "#2f6d85",
        "game_expend.lua", "leftactivelist[1]", note="动态重排；默认单项 55×50，纵向间距 62")
    add("right_ad_large", "右上大广告", "广告", 960, 94, 300, 150, "#e49b4d",
        "game_expend.lua", "limittimeactivitybg")
    add("right_ad_small", "右上下方广告", "广告", 960, 250, 300, 82, "#d47b43",
        "chat.lua", "imgChatAdvBG =", asset_hint="chatAdvBG.BMP")
    add("fast_activity", "限时/常驻活动圆钮", "活动", 1080, 330, 183, 83, "#7845aa",
        "game_main.lua", "FastEnterButton[i]", note="两个按钮时为 x=1080、1180")
    add("activity_popup", "活动展开面板", "活动", 966, 425, 293, 222, "#655078",
        "game_main.lua", "preview_ui =", visible=False)
    add("bottom_activity", "底部中央活动入口", "活动", 589, 653, 384, 128, "#a8603b",
        "game_hall.lua", "ResortSTZActivityIcon", note="单项 128×128，从右向左动态排列")
    add("play", "右下出击整组", "主操作", 996, 517, 276, 278, "#1475d1",
        "game_shop_hero_equip.lua", "btn_play =", note="包含主图、3 个透明热区、组队图、遮罩和特效", asset_hint="btn-play.png")
    add("chat", "左下聊天组", "聊天", 20, 685, 394, 94, "#31565f",
        "chat.lua", "UXChatRect =", note="跨 chat.lua 和 game_uxbutton.lua 的逻辑组")
    add("bottom_frame", "底部装饰条", "装饰", 0, 722, 1280, 78, "#202c3f",
        "game_shop_hero_equip.lua", "bgdowmimg =", locked=True)

    # Fine-grained controls. The broad nodes above are semantic groups; these nodes
    # expose the actual images/hit areas that must move together in the final patch.
    nav_labels = ["主页", "英雄", "商城", "活动", "日常", "装备", "修仙", "社团"]
    for i, label in enumerate(nav_labels, 1):
        add("nav_%02d" % i, "导航·" + label, "顶部/导航按钮", 50 + 62 * (i - 1), 0, 62, 58,
            "#5275a4", "game_shop_hero_equip.lua", "btn-nav%02d-01.png" % i,
            asset_hint="btn-nav%02d-01.png" % i)
    top_items = [
        ("money", "金币", 810, 14, 109, 22, "nav-assets-bg.png"),
        ("gold", "钻石", 919, 14, 109, 22, "nav-assets-bg.png"),
        ("setup", "设置", 1042, 13, 27, 27, "btn-nav-set01.png"),
        ("notice", "公告", 1080, 14, 26, 22, "btn-nav-notice01.png"),
        ("mail", "邮件", 1117, 16, 27, 22, "btn-nav-mail01.png"),
        ("friend", "好友", 1154, 14, 26, 26, "btn-nav-friend01.png"),
        ("portrait", "玩家头像", 1208, 21, 65, 64, "home-head-frame.png"),
        ("min", "最小化", 1233, 1, 18, 18, "btn-fewer01.png"),
        ("close", "关闭", 1254, 1, 18, 18, "btn-nav-close01.png"),
    ]
    for key, label, x, y, w, h, asset in top_items:
        add("top_" + key, label, "顶部/状态按钮", x, y, w, h, "#55708f",
            "game_shop_hero_equip.lua", asset, asset_hint=asset)
    for i in range(1, 10):
        add("left_activity_%02d" % i, "左侧入口 %d" % i, "活动/左侧入口", 8, 157 + 62 * (i - 1), 55, 50,
            "#2f8290", "game_expend.lua", "leftactivelist[%d]" % i,
            asset_hint="btn-home-left%02d-01.png" % i)
    for i, (key, x) in enumerate(((1, 1080), (3, 1180)), 1):
        add("fast_activity_%d" % i, "快速活动 %d" % i, "活动/右侧圆钮", x, 330, 83, 83,
            "#774aa8", "game_main.lua", "FastEnterButton[i]", asset_hint="btn%d-01.png" % key)
    for i in range(1, 8):
        index = i - 1
        x = 845 - 128 * (index % 4)
        y = 653 - 128 * (index // 4)
        add("bottom_activity_%d" % i, "底部活动 %d" % i, "活动/底部入口", x, y, 128, 128,
            "#a95d3d", "game_hall.lua", "entrancelist[%d]" % i,
            asset_hint="entrance%d_01.png" % i)
    play_items = [
        ("play_main", "出击主按钮", 1066, 582, 185, 185, "btn-play.png"),
        ("play_brawl", "出击热区·乱斗", 996, 639, 112, 156, "main_btn_yellow.png"),
        ("play_arena", "出击热区·竞技", 1003, 523, 135, 136, "main_btn_blue.png"),
        ("play_battle", "出击热区·战场", 1114, 517, 158, 105, "main_btn_red.png"),
        ("play_team", "出击·组队状态", 1059, 549, 200, 252, "btn-play-room.png"),
        ("play_mask", "出击·禁用遮罩", 1066, 582, 185, 185, "btn-play-mask.png"),
    ]
    for key, label, x, y, w, h, asset in play_items:
        add(key, label, "主操作/出击组件", x, y, w, h, "#1b74c5",
            "game_shop_hero_equip.lua", asset, asset_hint=asset,
            visible=key not in ("play_team", "play_mask"))
    decor = [
        ("bottom_bar", "底部背景条", 0, 746, 1280, 54, "upBK_hall.BMP"),
        ("bottom_left", "左下装饰", 0, 722, 123, 78, "LeftDown.BMP"),
        ("bottom_right", "右下装饰", 1157, 722, 123, 78, "RightDown.BMP"),
    ]
    for key, label, x, y, w, h, asset in decor:
        add(key, label, "装饰/底部组件", x, y, w, h, "#29384e",
            "game_shop_hero_equip.lua", asset, asset_hint=asset)

    return {
        "format": "300hero-layout/1",
        "gameDir": game_dir,
        "canvas": CANVAS,
        "state": "live2d",
        "options": {
            "auto_minimize_chat": True,
            "auto_accept_match": False,
            "camera_35": False,
            "clickable_surrender": False,
        },
        "nodes": n,
        "sources": {k: {"path": v.path, "pack": v.pack, "index": v.index, "md5": v.md5}
                    for k, v in sources.items()},
        "warnings": (["未找到：" + name for name in sorted(TARGET_LUA - set(sources))]),
    }


def analyze_game(game_dir: str) -> tuple[list[jc.Pack], dict[str, LuaSource], dict]:
    packs = jc.load_packs(game_dir)
    sources = find_lua_sources(packs)
    scene = build_scene(sources, game_dir)
    scene["packSummary"] = [
        {"name": p.base_name(), "count": len(p.entries), "ok": p.parse_ok,
         "error": p.error, "readOnly": p.read_only}
        for p in packs
    ]
    return packs, sources, scene


def layout_lua(scene: dict) -> str:
    lines = [
        "-- 300大厅布局编辑器生成；只保存布局参数，不包含游戏事件逻辑。",
        "-- 由接入补丁读取这些值并应用到原对象。",
        "HallLayout = {",
    ]
    for node in scene.get("nodes", []):
        key = re.sub(r"[^A-Za-z0-9_]", "_", node["id"])
        lines.append(
            "    %s = { visible = %d, x = %d, y = %d, width = %d, height = %d, scale = %.4f }," % (
                key, 1 if node.get("visible", True) else 0,
                round(node.get("x", 0)), round(node.get("y", 0)),
                round(node.get("width", 0)), round(node.get("height", 0)),
                float(node.get("scale", 1.0))))
    lines += ["}", ""]
    return "\n".join(lines)


def save_project(scene: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scene, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_project(scene: dict, sources: dict[str, LuaSource], folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    save_project(scene, folder / "大厅布局.halllayout.json")
    (folder / "hall_layout.lua").write_text(layout_lua(scene), encoding="utf-8")
    source_dir = folder / "原始Lua"
    source_dir.mkdir(exist_ok=True)
    for name, source in sources.items():
        (source_dir / name).write_text(source.text, encoding="utf-8")
    manifest = {
        "format": "300hero-export/1",
        "gameDir": scene.get("gameDir"),
        "files": scene.get("sources", {}),
        "note": "包含布局配置、HallLayout Lua、来源清单和用于审查的原始 Lua。",
    }
    (folder / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return folder

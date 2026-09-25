from __future__ import annotations

import difflib
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import jmp_core as jc
from hall_scene import LuaSource


MARK_BEGIN = "--[[ 300HERO_LAYOUT_EDITOR_BEGIN ]]"
MARK_END = "--[[ 300HERO_LAYOUT_EDITOR_END ]]"
INLINE_MASK_MARK = "-- 300HERO_LAYOUT_EDITOR_INLINE_HOME_MASK"


@dataclass
class PatchFile:
    name: str
    internal_path: str
    pack: str
    index: int
    original: str
    patched: str
    encoding: str = "gb18030"

    @property
    def changed(self):
        return self.original != self.patched

    @property
    def diff(self):
        return "".join(difflib.unified_diff(
            self.original.splitlines(True), self.patched.splitlines(True),
            fromfile=self.internal_path + " (原始)", tofile=self.internal_path + " (大厅布局补丁)"))


FILE_OBJECTS = {
    "game_hall.lua": {
        "live2d_pop": "Live2D_Pop", "live2d_bubble": "Live2D_Bubble",
        "live2d_dialog": "dlg_live2d.BK",
        "live2d_switch": "btn_live2d", "skin_switch": "btn_switchsuper",
        **{"bottom_activity_%d" % i: "entrancelist[%d]" % i for i in range(1, 8)},
    },
    "game_expend.lua": {
        "top_banner": "NewTower", "right_ad_large": "limittimeactivitybg",
        **{"left_activity_%02d" % i: "leftactivelist[%d]" % i for i in range(1, 10)},
    },
    "game_main.lua": {
        "fast_activity_1": "FastEnterButton[1]", "fast_activity_2": "FastEnterButton[2]",
        "activity_popup": "preview_ui",
    },
    "game_shop_hero_equip.lua": {
        "nav_01": "btn_webSite", "nav_02": "btn_hero", "nav_03": "btn_shop",
        "nav_04": "btn_active", "nav_05": "btn_signtask", "nav_06": "btn_equip",
        "nav_07": "btn_xiuxian", "nav_08": "btn_societies",
        "top_money": "show_money", "top_gold": "show_gold", "top_setup": "Btn_setup",
        "top_notice": "Updatebk", "top_mail": "btn_mail", "top_friend": "btn_friend",
        "top_portrait": "btn_headPicImg", "top_min": "Btn_min", "top_close": "Btn_close",
        "play_main": "btn_play", "play_brawl": "btn_play_luandou",
        "play_arena": "btn_play_jingji", "play_battle": "btn_play_zhanchang",
        "play_team": "btn_uxfightteam", "play_mask": "btn_uxfightmask",
        "bottom_bar": "bgdowmimg",
    },
    "chat.lua": {"right_ad_small": "imgChatAdvBG", "chat": "wndchatbackground"},
    "game_uxbutton.lua": {},
}


WRAPPERS = {
    "game_hall.lua": ["InitMainGame_hall", "ResortSTZActivityIcon", "SendIsSuperToHall", "ShowLive2dDlg"],
    "game_expend.lua": ["Init_MenuListpart_expend", "ResetPosition_ActivityBtn", "SetExpend_NewTowerEnter", "SetUXActivityScrollShow"],
    "game_main.lua": ["Init_UI_AllActivity", "SetActivity_FastEnterButtonReset"],
    "game_shop_hero_equip.lua": ["InitGame_FourpartUI", "SetUXHallPlayVisible", "SetUXHallTeamIsVisible", "SetUXHallMaskIsVisible", "ForbidBtn_societies"],
    "chat.lua": ["CreateChatWindow", "SetChatInputFocus"],
    "game_uxbutton.lua": ["InitUXHallButtonUI", "SetUXHallButtonChatButton"],
}


def _lua_bool(value):
    return 1 if value else 0


def _clean_previous(text: str) -> str:
    pattern = re.compile(r"\n?" + re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END) + r"\n?", re.S)
    text = pattern.sub("\n", text)
    text = re.sub(r"^\s*mask:SetVisible\(0\)\s*" + re.escape(INLINE_MASK_MARK) + r"\s*\r?\n?", "", text, flags=re.M)
    return text.rstrip() + "\n"


def _apply_inline_edits(name: str, text: str, scene: dict) -> str:
    """Apply edits that must run while an original Lua local is still in scope."""
    if name != "game_hall.lua":
        return text
    edited = text
    node = next((item for item in scene.get("nodes", []) if item.get("id") == "home_mask"), None)
    if node and not node.get("visible", True):
        pattern = r"(^\s*mask:SetTouchEnabled\(0\)\s*$)"
        replacement = r"\1\n    mask:SetVisible(0) " + INLINE_MASK_MARK
        edited, count = re.subn(pattern, replacement, edited, count=1, flags=re.M)
        if count != 1:
            raise ValueError("无法定位大厅 home-mask 的局部初始化位置，已停止生成补丁")
    return edited


def _apply_lines(scene: dict, mapping: dict[str, str]) -> list[str]:
    nodes = {node["id"]: node for node in scene.get("nodes", [])}
    lines = []
    for node_id, expression in mapping.items():
        node = nodes.get(node_id)
        if not node:
            continue
        x, y = round(node.get("x", 0)), round(node.get("y", 0))
        scale = float(node.get("scale", 1.0))
        w = max(1, round(float(node.get("width", 1)) * scale))
        h = max(1, round(float(node.get("height", 1)) * scale))
        visible = _lua_bool(node.get("visible", True))
        lines.append("    __hall_set(%s, %d, %d, %d, %d, %d)" % (expression, x, y, w, h, visible))
    return lines


def _block(name: str, scene: dict) -> str:
    mapping = FILE_OBJECTS.get(name, {})
    apply_lines = _apply_lines(scene, mapping)
    auto_minimize_chat = bool((scene.get("options") or {}).get("auto_minimize_chat"))
    if name == "game_uxbutton.lua":
        nodes = {node["id"]: node for node in scene.get("nodes", [])}
        chat = nodes.get("chat")
        if chat:
            apply_lines += [
                "    __hall_set(btn_chat, %d, %d, 86, 30, %d)" % (
                    round(chat["x"]), round(chat["y"] + 64), _lua_bool(chat.get("visible", True))),
                "    __hall_set(show_onlinepeople, %d, %d, 30, 27, %d)" % (
                    round(chat["x"] + 101), round(chat["y"] + 66), _lua_bool(chat.get("visible", True))),
            ]
    wrappers = []
    for index, function in enumerate(WRAPPERS.get(name, []), 1):
        safe = re.sub(r"\W", "_", function)
        wrappers += [
            "local __hall_old_%s = %s" % (safe, function),
            "if __hall_old_%s ~= nil then" % safe,
            "    %s = function(...)" % function,
            "        local __hall_result = {__hall_old_%s(...)}" % safe,
            "        __hall_apply_%s()" % re.sub(r"\W", "_", name),
            "        return unpack(__hall_result)",
            "    end",
            "end",
        ]
    # The game can reopen the large chat window after CreateChatWindow returns,
    # when the hall button UI finishes initializing, and whenever another scene
    # switches the hall controls back on.  Hook those lifecycle points instead
    # of continuously overriding SetUXHallButtonChatButton: the latter would
    # make the user's manual "expand chat" click impossible.
    if auto_minimize_chat and name == "chat.lua":
        wrappers += [
            "local __hall_chat_old_CreateChatWindow = CreateChatWindow",
            "if __hall_chat_old_CreateChatWindow ~= nil then",
            "    CreateChatWindow = function(...)",
            "        local __hall_result = {__hall_chat_old_CreateChatWindow(...)}",
            "        local __hall_chat_window = __hall_result[1]",
            "        if __hall_chat_window ~= nil and __hall_chat_window.HideChat ~= nil then",
            "            __hall_chat_window.HideChat()",
            "        end",
            "        return unpack(__hall_result)",
            "    end",
            "end",
            # ClearOutChat and several engine-side scene transitions call
            # SetChatInputFocus(1), whose stock implementation always expands
            # the large chat panel.  Collapse it again after that automatic
            # focus path.  The small chat button remains usable because its
            # click handler calls SetUXHallButtonChatButton(0) directly.
            "local __hall_chat_old_SetChatInputFocus = SetChatInputFocus",
            "if __hall_chat_old_SetChatInputFocus ~= nil then",
            "    SetChatInputFocus = function(...)",
            "        local __hall_result = {__hall_chat_old_SetChatInputFocus(...)}",
            "        if SetUXHallButtonChatButton ~= nil then SetUXHallButtonChatButton(1) end",
            "        return unpack(__hall_result)",
            "    end",
            "end",
        ]
    if auto_minimize_chat and name == "game_uxbutton.lua":
        wrappers += [
            "local __hall_chat_old_InitUXHallButtonUI = InitUXHallButtonUI",
            "if __hall_chat_old_InitUXHallButtonUI ~= nil then",
            "    InitUXHallButtonUI = function(...)",
            "        local __hall_result = {__hall_chat_old_InitUXHallButtonUI(...)}",
            "        if SetUXHallButtonChatButton ~= nil then SetUXHallButtonChatButton(1) end",
            "        return unpack(__hall_result)",
            "    end",
            "end",
            "local __hall_chat_old_SetUXHallButtonIsVisible = SetUXHallButtonIsVisible",
            "if __hall_chat_old_SetUXHallButtonIsVisible ~= nil then",
            "    SetUXHallButtonIsVisible = function(flag, ...)",
            "        local __hall_result = {__hall_chat_old_SetUXHallButtonIsVisible(flag, ...)}",
            "        if flag == 1 and SetUXHallButtonChatButton ~= nil then SetUXHallButtonChatButton(1) end",
            "        return unpack(__hall_result)",
            "    end",
            "end",
        ]
    apply_name = re.sub(r"\W", "_", name)
    return "\n".join([
        MARK_BEGIN,
        "-- 自动生成。保留原按钮事件，只覆盖布局；visible=1 不强制打开游戏当前隐藏的状态。",
        "local function __hall_set(obj, x, y, w, h, visible)",
        "    if obj ~= nil then",
        "        obj:SetPosition(x, y)",
        "        obj:SetWH(w, h)",
        "        if visible == 0 then obj:SetVisible(0) end",
        "    end",
        "end",
        "local function __hall_apply_%s()" % apply_name,
        *(apply_lines or ["    -- 此文件当前没有独立对象，只保留动态包装入口"]),
        "end",
        *wrappers,
        MARK_END,
        "",
    ])


def build_patches(scene: dict, sources: dict[str, LuaSource]) -> list[PatchFile]:
    patches = []
    for name in FILE_OBJECTS:
        source = sources.get(name)
        if not source:
            continue
        original = _clean_previous(source.text)
        patched = _apply_inline_edits(name, original, scene) + "\n" + _block(name, scene)
        patches.append(PatchFile(name, source.path, source.pack, source.index, original, patched))
    return patches


def export_patches(patches: list[PatchFile], folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    lua_dir = folder / "patched_lua"
    lua_dir.mkdir(exist_ok=True)
    all_diff = []
    manifest = []
    for patch in patches:
        raw = patch.patched.encode(patch.encoding)
        (lua_dir / patch.name).write_bytes(raw)
        all_diff.append(patch.diff)
        manifest.append({"name": patch.name, "internalPath": patch.internal_path,
                         "pack": patch.pack, "index": patch.index,
                         "md5": hashlib.md5(raw).hexdigest(), "size": len(raw)})
    (folder / "layout.patch.diff").write_text("\n".join(all_diff), encoding="utf-8")
    (folder / "patch_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return folder


def locate_entry(packs: list[jc.Pack], patch: PatchFile):
    target = patch.internal_path.replace('/', '\\').lower()
    for pack in packs:
        for entry in pack.entries:
            if entry.path.replace('/', '\\').lower() == target:
                return pack, entry
    raise FileNotFoundError("目标 Lua 已不在 JMP 中：" + patch.internal_path)


def apply_patches(scene: dict, patches: list[PatchFile], packs: list[jc.Pack], backup_dir: Path) -> list[dict]:
    results = []
    for patch in patches:
        pack, entry = locate_entry(packs, patch)
        current = jc.read_entry(pack, entry)
        current_text = None
        for encoding in ("gb18030", "utf-8-sig", "utf-8"):
            try:
                current_text = current.decode(encoding)
                break
            except UnicodeDecodeError:
                pass
        if current_text is None:
            raise ValueError("Lua 编码无法识别：" + patch.internal_path)
        # Rebase the generated block onto the latest target file to preserve any
        # unrelated edits made after the editor first analyzed the game.
        clean_text = _clean_previous(current_text)
        new_text = _apply_inline_edits(patch.name, clean_text, scene) + "\n" + _block(patch.name, scene)
        new_raw = new_text.encode("gb18030")
        result = jc.patch_entry(pack, entry, new_raw, str(backup_dir), allow_overflow=True)
        checked = jc.read_entry(pack, entry)
        if checked != new_raw:
            raise IOError("写入后校验失败：" + patch.internal_path)
        results.append(result)
    return results


def apply_scene(scene: dict, sources: dict[str, LuaSource], packs: list[jc.Pack], backup_dir: Path):
    return apply_patches(scene, build_patches(scene, sources), packs, backup_dir)


def restore_all(backup_dir: Path) -> list[dict]:
    results = []
    for item in jc.list_backups(str(backup_dir)):
        results.append(jc.restore_entry(item["_file"]))
    return results

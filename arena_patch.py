from __future__ import annotations

from dataclasses import dataclass
import difflib

from hall_scene import LuaSource
from lua_patch import PatchFile, locate_entry
import jmp_core as jc


MARK_BEGIN = "--[[ ARENA_LAYOUT_EDITOR_BEGIN ]]"
MARK_END = "--[[ ARENA_LAYOUT_EDITOR_END ]]"


def _clean(text: str) -> str:
    a = text.find(MARK_BEGIN)
    b = text.find(MARK_END)
    if a >= 0 and b >= a:
        return (text[:a].rstrip() + "\n" + text[b + len(MARK_END):].lstrip()).rstrip() + "\n"
    return text


def _lua_node(node):
    return "    __arena_set(%s, %d, %d, %d, %d, %d, %.4f, %s)" % (
        node["runtimeRoot"], round(node["x"]), round(node["y"]), round(node["width"]),
        round(node["height"]), 1 if node.get("visible", True) else 0,
        float(node.get("scale", 1)), repr(node.get("anchor", "top-left")))


def _block(scene):
    lines = [MARK_BEGIN,
        "local function __arena_set(obj, sw, sh, dx, dy, w, h, visible, scale, anchor)",
        "    if obj == nil then return end",
        "    local x, y = dx, dy",
        "    if anchor == 'top-center' or anchor == 'bottom-center' then x = (sw - 1920) / 2 + dx end",
        "    if anchor == 'top-right' or anchor == 'right-middle' or anchor == 'bottom-right' then x = sw - (1920 - dx) end",
        "    if anchor == 'left-middle' or anchor == 'right-middle' then y = (sh - 1080) / 2 + dy end",
        "    if anchor == 'bottom-left' or anchor == 'bottom-center' or anchor == 'bottom-right' then y = sh - (1080 - dy) end",
        "    obj:MoveWindow(x, y, w * scale, h * scale)",
        "    obj:SetVisible(visible)", "end", "local function __arena_apply(sw, sh)"]
    lines += [_lua_node(n).replace("__arena_set(", "__arena_set(").replace(", ", ", sw, sh, ", 1) for n in scene.get("nodes", [])]
    lines += ["end", "local __arena_old_sizechange_movewindow = sizechange_movewindow",
              "if __arena_old_sizechange_movewindow ~= nil then",
              "    function sizechange_movewindow(width, height, ...)",
              "        local r = {__arena_old_sizechange_movewindow(width, height, ...)}",
              "        __arena_apply(width, height)", "        return unpack(r)", "    end", "end",
              MARK_END, ""]
    return "\n".join(lines)


def build_arena_patches(scene: dict, sources: dict[str, LuaSource]):
    source = sources.get("battle.lua")
    if not source:
        raise ValueError("未找到竞技场 battle.lua，无法生成布局补丁")
    original = _clean(source.text)
    patched = original.rstrip() + "\n\n" + _block(scene)
    return [PatchFile("battle.lua", source.path, source.pack, source.index, original, patched)]


def apply_arena(scene, sources, packs, backup_dir):
    results = []
    for patch in build_arena_patches(scene, sources):
        pack, entry = locate_entry(packs, patch)
        current = jc.read_entry(pack, entry)
        text = None
        for encoding in ("gb18030", "utf-8-sig", "utf-8"):
            try:
                text = current.decode(encoding)
                break
            except UnicodeDecodeError:
                pass
        if text is None:
            raise ValueError("Lua 编码无法识别：" + patch.internal_path)
        new_text = _clean(text).rstrip() + "\n\n" + _block(scene)
        new_raw = new_text.encode("gb18030")
        result = jc.patch_entry(pack, entry, new_raw, str(backup_dir), allow_overflow=True)
        if jc.read_entry(pack, entry) != new_raw:
            raise IOError("写入后校验失败：" + patch.internal_path)
        results.append(result)
    return results

import unittest

from hall_scene import LuaSource
from lua_patch import (ACTIVITY_SKIP_MARK, NOTICE_BEGIN, _apply_inline_edits,
                       _clean_previous, _restore_activity_request, build_patches,
                       _restore_deferred_notice, _suppress_activity_request)


NOTICE_SOURCE = """function Init_MenuListpart_up(wnd)
    UpdateWnd = wnd:AddImage(path_loltimertower .. "BK3.BMP", 205, 131, 870, 539)
    UpdateWnd:SetVisible(0)
    CloseWndBtn.script[XE_LBUP] = function()
        SetUpdateWndIsVisible(0)
        XReqNeedShowActivity(249)
    end
    UpdateShopSkinWnd = CreateWindow(UpdateWnd.id, 0, 0, 870, 539)
    CreateUpdateShopSkinWnd(UpdateShopSkinWnd)
end

function Init_MenuListpart_common(wnd)
    Updatebk.script[XE_LBUP] = function()
        SetUpdateWndIsVisible(1)
    end
end

function SetUpdateWndIsVisible(flag)
    if UpdateWnd ~= nil then
        UpdateWnd:SetVisible(flag)
    end
end
"""


class NoticeOptionTests(unittest.TestCase):
    def test_notice_is_initialized_only_on_manual_click_and_reversible(self):
        for newline in ("\n", "\r\n"):
            with self.subTest(newline=repr(newline)):
                source = NOTICE_SOURCE.replace("\n", newline)
                changed = _apply_inline_edits(
                    "game_shop_hero_equip.lua", source,
                    {"options": {"suppress_login_notice": True}},
                )
                startup = changed.split("function Init_MenuListpart_common(wnd)", 1)[0]
                self.assertIn(NOTICE_BEGIN, changed)
                self.assertNotIn("UpdateWnd = wnd:AddImage", startup.split(NOTICE_BEGIN, 1)[0])
                self.assertIn("__hall_notice_load(g_up)" + newline
                              + "        SetUpdateWndIsVisible(1, true)", changed)
                self.assertIn("if flag >= 1 and not manual then return end", changed)
                self.assertIn(ACTIVITY_SKIP_MARK, changed)
                self.assertEqual(_restore_activity_request(_restore_deferred_notice(changed)), source)

    def test_disabled_option_restores_the_original_function(self):
        changed = _apply_inline_edits(
            "game_shop_hero_equip.lua", NOTICE_SOURCE,
            {"options": {"suppress_login_notice": True}},
        )
        restored = _apply_inline_edits(
            "game_shop_hero_equip.lua", _clean_previous(changed),
            {"options": {"suppress_login_notice": False}},
        )
        self.assertEqual(restored, NOTICE_SOURCE)

    def test_escape_activity_request_is_removed_and_restored(self):
        for newline in ("\n", "\r\n"):
            with self.subTest(newline=repr(newline)):
                source = ("if GetUpdateWndIsVisible() == 1 then" + newline
                          + "    SetUpdateWndIsVisible(0)" + newline
                          + "\t\tXReqNeedShowActivity(249)" + newline
                          + "end" + newline)
                changed = _suppress_activity_request(source)
                self.assertIn(ACTIVITY_SKIP_MARK, changed)
                self.assertNotIn("\t\tXReqNeedShowActivity(249)", changed)
                self.assertEqual(_restore_activity_request(changed), source)

    def test_login_script_is_patched_only_while_option_is_enabled(self):
        path = r"..\data\script\login\gamedef.lua"
        original = "XReqNeedShowActivity(249)\n"
        source = LuaSource(path, "Data12.jmp", 4, original, "unused")
        enabled = {"options": {"suppress_login_notice": True}, "nodes": []}
        disabled = {"options": {"suppress_login_notice": False}, "nodes": []}

        self.assertEqual(build_patches(disabled, {"gamedef.lua": source}), [])
        applied = build_patches(enabled, {"gamedef.lua": source})
        self.assertEqual(len(applied), 1)
        self.assertIn(ACTIVITY_SKIP_MARK, applied[0].patched)

        updated = LuaSource(path, "Data12.jmp", 4, applied[0].patched, "unused")
        restored = build_patches(disabled, {"gamedef.lua": updated})
        self.assertEqual(len(restored), 1)
        self.assertNotIn(ACTIVITY_SKIP_MARK, restored[0].patched)


if __name__ == "__main__":
    unittest.main()

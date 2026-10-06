import unittest
from unittest.mock import patch

import additional_options
import hall_scene
import jmp_core
import lua_patch


class PackSelectionTests(unittest.TestCase):
    def test_lua_reads_and_writes_follow_actual_pack_order(self):
        internal_path = r"..\data\script\game_shop_hero_equip.lua"
        packs = []
        for number in (3, 12):
            pack = jmp_core.Pack(file=f"Data{number}.jmp", parse_ok=True)
            pack.entries = [jmp_core.Entry(pack.file, 0, internal_path, 0, 1, 1, "0" * 32)]
            packs.append(pack)

        with patch.object(jmp_core, "read_entry", return_value=b"lua"):
            source = hall_scene.find_lua_sources(packs)["game_shop_hero_equip.lua"]

        self.assertEqual(source.pack, "Data12.jmp")
        self.assertIs(additional_options._locate(packs, internal_path)[0], packs[1])
        example = lua_patch.PatchFile("game_shop_hero_equip.lua", internal_path,
                                      source.pack, 0, "", "")
        self.assertIs(lua_patch.locate_entry(packs, example)[0], packs[1])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import argparse
import io
import json
import mimetypes
import os
import sys
import threading
import webbrowser
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from PIL import Image
import jmp_core as jc

from hall_scene import analyze_game, export_project, save_project
from resource_export import extract_lobby_resources, load_asset_manifest
from lua_patch import apply_scene, build_patches, export_patches, restore_all
from additional_options import apply_options, build_option_changes, export_options, preview_options
from arena_scene import analyze_arena, export_arena_project
from arena_patch import apply_arena, build_arena_patches
from settings_store import choose_game_dir, has_jmp_files, load_settings, save_settings
from version_history import snapshot_current_version


FROZEN = bool(getattr(sys, "frozen", False))
BUNDLE_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
ROOT = Path(sys.executable).resolve().parent if FROZEN else Path(__file__).resolve().parent
WEB = BUNDLE_ROOT / "web"
ASSETS = ROOT / "assets"
GAME_BACKUPS = ROOT / "game_backups"
OPTION_BASELINES = ROOT / "option_baselines"
OPTION_TEMPLATES = BUNDLE_ROOT / "option_templates"
DEFAULT_GAME_DIR = r"D:\JumpGame\300Hero"
SETTINGS_FILE = ROOT / "config" / "settings.json"
VERSION_HISTORY = ROOT / "version_history"


class State:
    def __init__(self, game_dir: str):
        self.lock = threading.RLock()
        self.game_dir = game_dir
        self.packs = []
        self.sources = {}
        self.scene = None
        self.arena_sources = {}
        self.arena_scene = None
        self.error = ""
        self.resource_index = {}
        self.resource_cache = {}
        self.asset_manifest = load_asset_manifest(ASSETS)

    def analyze(self, game_dir: str | None = None):
        with self.lock:
            if game_dir:
                self.game_dir = game_dir
            if not has_jmp_files(self.game_dir):
                raise FileNotFoundError("所选目录中没有 Data*.jmp，请重新选择游戏目录")
            self.packs, self.sources, self.scene = analyze_game(self.game_dir)
            self.arena_sources, self.arena_scene = analyze_arena(self.packs, self.game_dir)
            self.resource_index = {}
            for pack in self.packs:
                for entry in pack.entries:
                    self.resource_index.setdefault(entry.path.replace('/', '\\').lower(), (pack, entry))
            self.resource_cache.clear()
            self.error = ""
            settings = load_settings(SETTINGS_FILE)
            settings["gameDir"] = self.game_dir
            save_settings(SETTINGS_FILE, settings)
            return self.scene

    def extract_assets(self):
        if not self.packs or not self.sources:
            self.analyze()
        self.asset_manifest = extract_lobby_resources(self.packs, self.sources, ASSETS)
        return self.asset_manifest

    def resource(self, hint: str) -> tuple[bytes, str, str]:
        key = hint.strip().replace('/', '\\').lower()
        if not key:
            raise ValueError("缺少资源路径或名称")
        cached = self.resource_cache.get(key)
        if cached:
            return cached
        if self.asset_manifest:
            local = []
            for item in self.asset_manifest.get("resources", []):
                internal = item["internalPath"].replace('/', '\\').lower()
                if internal == key or internal.endswith('\\' + key) or key in internal:
                    if item.get("preview"):
                        local.append((internal, item))
            local.sort(key=lambda value: (
                '\\pve\\' in value[0] or '\\tiyan\\' in value[0],
                not value[0].endswith(key), len(value[0])))
            if local:
                item = local[0][1]
                file = ASSETS / "web" / Path(item["preview"])
                if file.is_file():
                    mime = {'.png': 'image/png', '.gif': 'image/gif', '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg'}.get(file.suffix.lower(), 'application/octet-stream')
                    result = (file.read_bytes(), mime, item["internalPath"])
                    self.resource_cache[key] = result
                    return result
        choices = []
        for path, pair in self.resource_index.items():
            if path == key or path.endswith('\\' + key) or key in path:
                choices.append((path, pair))
        if not choices:
            raise FileNotFoundError("JMP 中未找到资源：" + hint)
        choices.sort(key=lambda item: (
            '\\pve\\' in item[0] or '\\tiyan\\' in item[0],
            not item[0].endswith(key), len(item[0])))
        last_error = None
        for path, (pack, entry) in choices[:30]:
            try:
                raw = jc.read_entry(pack, entry)
                ext = Path(path).suffix.lower()
                if ext in ('.png', '.gif', '.jpg', '.jpeg'):
                    mime = {'.png': 'image/png', '.gif': 'image/gif',
                            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}[ext]
                    result = (raw, mime, entry.path)
                else:
                    image = Image.open(io.BytesIO(raw)).convert('RGBA')
                    output = io.BytesIO()
                    image.save(output, format='PNG')
                    result = (output.getvalue(), 'image/png', entry.path)
                self.resource_cache[key] = result
                return result
            except Exception as exc:
                last_error = exc
        raise ValueError("资源无法转换为网页图片：%s (%s)" % (hint, last_error))


def json_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")


def make_handler(state: State):
    class Handler(BaseHTTPRequestHandler):
        server_version = "300HeroEditor/0.1"

        def log_message(self, fmt, *args):
            # Keep the release console quiet during normal browser/resource requests.
            return

        def send_data(self, status: int, data: bytes, content_type: str):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def send_json(self, value, status=200):
            self.send_data(status, json_bytes(value), "application/json; charset=utf-8")

        def body_json(self):
            length = int(self.headers.get("Content-Length", "0"))
            if length > 16 * 1024 * 1024:
                raise ValueError("请求过大")
            return json.loads(self.rfile.read(length) or b"{}")

        def do_GET(self):
            parsed = urlparse(self.path)
            path = unquote(parsed.path)
            if path == "/api/status":
                self.send_json({"gameDir": state.game_dir, "ready": state.scene is not None,
                                "error": state.error})
                return
            if path == "/api/select-game-dir":
                selected = choose_game_dir(state.game_dir)
                if not selected:
                    self.send_json({"error": "没有选择游戏目录"}, 400)
                    return
                if not has_jmp_files(selected):
                    self.send_json({"error": "所选目录中没有 Data*.jmp"}, 400)
                    return
                scene = state.analyze(selected)
                self.send_json({"gameDir": state.game_dir, "scene": scene})
                return
            if path == "/api/scene":
                if state.scene is None:
                    try:
                        state.analyze()
                    except Exception as exc:
                        state.error = str(exc)
                        self.send_json({"error": str(exc)}, 500)
                        return
                mode = parse_qs(parsed.query).get('mode', ['hall'])[0]
                self.send_json(state.arena_scene if mode == 'arena' else state.scene)
                return
            if path == "/api/assets":
                self.send_json(state.asset_manifest or {"resourceCount": 0, "previewCount": 0,
                                                         "totalBytes": 0, "resources": []})
                return
            if path == "/api/projects":
                folder = ROOT / "projects"
                folder.mkdir(exist_ok=True)
                items = []
                for file in sorted(list(folder.glob("*.halllayout.json")) + list(folder.glob("*.arenalayout.json")),
                                   key=lambda value: value.stat().st_mtime, reverse=True):
                    suffix = '.arenalayout.json' if file.name.endswith('.arenalayout.json') else '.halllayout.json'
                    items.append({"name": file.name[:-len(suffix)], "file": file.name,
                                  "modified": int(file.stat().st_mtime), "size": file.stat().st_size})
                self.send_json({"projects": items})
                return
            if path == "/api/resource":
                try:
                    hint = parse_qs(parsed.query).get('hint', [''])[0]
                    raw, mime, _internal = state.resource(hint)
                    self.send_data(200, raw, mime)
                except FileNotFoundError as exc:
                    self.send_json({"error": str(exc)}, 404)
                except Exception as exc:
                    self.send_json({"error": str(exc)}, 500)
                return
            rel = "index.html" if path in ("", "/") else path.lstrip("/")
            target = (WEB / rel).resolve()
            if WEB.resolve() not in target.parents and target != WEB.resolve():
                self.send_error(HTTPStatus.FORBIDDEN)
                return
            if not target.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            mime = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            if mime.startswith("text/") or mime in ("application/javascript", "application/json"):
                mime += "; charset=utf-8"
            self.send_data(200, target.read_bytes(), mime)

        def do_POST(self):
            parsed = urlparse(self.path)
            path = parsed.path
            try:
                body = self.body_json()
                if path == "/api/analyze":
                    scene = state.analyze(body.get("gameDir") or state.game_dir)
                    self.send_json(state.arena_scene if body.get("mode") == "arena" else scene)
                    return
                if path == "/api/extract-assets":
                    self.send_json(state.extract_assets())
                    return
                if path == "/api/load-project":
                    name = Path(str(body.get("file", ""))).name
                    if not (name.endswith(".halllayout.json") or name.endswith(".arenalayout.json")):
                        raise ValueError("不是有效的布局项目文件")
                    file = ROOT / "projects" / name
                    if not file.is_file():
                        raise FileNotFoundError("项目不存在：" + name)
                    loaded = json.loads(file.read_text(encoding="utf-8"))
                    if loaded.get("format") not in ("300hero-layout/1", "300arena-layout/1") or not isinstance(loaded.get("nodes"), list):
                        raise ValueError("项目格式无效")
                    self.send_json(loaded)
                    return
                if path == "/api/preview-patch":
                    scene = body.get("scene") or body
                    arena = scene.get("mode") == "arena"
                    patches = build_arena_patches(scene, state.arena_sources) if arena else build_patches(scene, state.sources)
                    files = [{"name": p.name, "path": p.internal_path,
                                                "pack": p.pack, "index": p.index,
                                                "changed": p.changed, "diff": p.diff}
                                               for p in patches]
                    files += [] if arena else [{"name": x["option"], "path": x["path"], "pack": x["pack"],
                               "index": None, "changed": True, "diff": x["diff"]}
                              for x in preview_options(scene, state.packs, OPTION_TEMPLATES, OPTION_BASELINES)]
                    self.send_json({"files": files})
                    return
                if path == "/api/generate-patch":
                    scene = body.get("scene") or body
                    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    arena = scene.get("mode") == "arena"
                    folder = export_patches(build_arena_patches(scene, state.arena_sources) if arena else build_patches(scene, state.sources),
                                            ROOT / "exports" / (("竞技场布局补丁_" if arena else "游戏Lua补丁_") + stamp))
                    extras = [] if arena else export_options(scene, state.packs, OPTION_TEMPLATES, OPTION_BASELINES, folder)
                    self.send_json({"ok": True, "path": str(folder), "additionalOptions": len(extras)})
                    return
                if path == "/api/apply-game":
                    scene = body.get("scene") or body
                    arena = scene.get("mode") == "arena"
                    patches = build_arena_patches(scene, state.arena_sources) if arena else build_patches(scene, state.sources)
                    history_targets = list(patches)
                    if not arena:
                        from types import SimpleNamespace
                        option_changes = build_option_changes(scene, state.packs, OPTION_TEMPLATES,
                                                              OPTION_BASELINES, False)
                        history_targets += [SimpleNamespace(internal_path=x["path"]) for x in option_changes]
                    previous_version = snapshot_current_version(history_targets, state.packs,
                                                                VERSION_HISTORY, state.game_dir)
                    results = apply_arena(scene, state.arena_sources, state.packs, GAME_BACKUPS) if arena else apply_scene(scene, state.sources, state.packs, GAME_BACKUPS)
                    option_results = [] if arena else apply_options(scene, state.packs, OPTION_TEMPLATES,
                                                                    OPTION_BASELINES, GAME_BACKUPS)
                    results += option_results
                    # Reload indexes/source texts so future previews use the patched files.
                    state.analyze(state.game_dir)
                    self.send_json({"ok": True, "count": len(results), "results": results,
                                    "backupDir": str(GAME_BACKUPS), "previousVersion": str(previous_version)})
                    return
                if path == "/api/restore-game":
                    results = restore_all(GAME_BACKUPS)
                    state.analyze(state.game_dir)
                    self.send_json({"ok": True, "count": len(results), "results": results})
                    return
                if path == "/api/save":
                    scene = body.get("scene") or body
                    name = body.get("name", "大厅布局项目") if isinstance(body, dict) else "大厅布局项目"
                    safe = "".join(c for c in name if c not in '<>:"/\\|?*').strip() or "大厅布局项目"
                    suffix = ".arenalayout.json" if scene.get("mode") == "arena" else ".halllayout.json"
                    path_out = save_project(scene, ROOT / "projects" / (safe + suffix))
                    self.send_json({"ok": True, "path": str(path_out)})
                    return
                if path == "/api/export":
                    scene = body.get("scene") or body
                    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    if scene.get("mode") == "arena":
                        folder = export_arena_project(scene, state.arena_sources, ROOT / "exports" / ("竞技场布局_" + stamp))
                    else:
                        folder = export_project(scene, state.sources, ROOT / "exports" / ("大厅布局_" + stamp))
                    self.send_json({"ok": True, "path": str(folder)})
                    return
                self.send_json({"error": "未知接口"}, 404)
            except Exception as exc:
                self.send_json({"error": str(exc)}, 500)

    return Handler


def main():
    parser = argparse.ArgumentParser(description="300英雄大厅布局编辑器")
    parser.add_argument("--game-dir", default=None)
    parser.add_argument("--port", type=int, default=0, help="0=自动选择空闲端口")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    settings = load_settings(SETTINGS_FILE)
    requested = args.game_dir or settings.get("gameDir") or DEFAULT_GAME_DIR
    if not has_jmp_files(requested):
        requested = choose_game_dir(requested) or requested
    state = State(os.path.abspath(requested))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(state))
    url = "http://127.0.0.1:%d/" % server.server_port
    print("300大厅布局编辑器已启动：" + url)
    print("游戏目录：" + state.game_dir)
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

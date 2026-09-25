from pathlib import Path

from hall_scene import analyze_game
from resource_export import extract_lobby_resources


def main():
    root = Path(__file__).resolve().parent
    packs, sources, _scene = analyze_game(r"D:\JumpGame\300Hero")
    def progress(done, total, path):
        print("[%d/%d] %s" % (done, total, path))
    result = extract_lobby_resources(packs, sources, root / "assets", progress)
    print("完成：%d 个资源，%d 个网页预览，%.2f MiB" % (
        result["resourceCount"], result["previewCount"], result["totalBytes"] / 1024 / 1024))


if __name__ == "__main__":
    main()

"""4x4グリッドのスタンプ一覧画像を、LINE公式サイズ(370x320)の01.png～16.pngに分割する。"""
import argparse
import os

from PIL import Image

GRID = 4
STICKER_SIZE = (370, 320)
DEFAULT_SOURCE = "source_grid.png"
DEFAULT_OUTPUT = "split_stickers"


def split(source, output, grid=GRID, size=STICKER_SIZE):
    img = Image.open(source).convert("RGBA")
    width, height = img.size
    os.makedirs(output, exist_ok=True)
    paths = []
    for index in range(grid * grid):
        row, col = divmod(index, grid)
        box = (
            col * width // grid,
            row * height // grid,
            (col + 1) * width // grid,
            (row + 1) * height // grid,
        )
        cell = img.crop(box)
        scale = min(size[0] / cell.width, size[1] / cell.height)
        new_size = (max(1, round(cell.width * scale)), max(1, round(cell.height * scale)))
        cell = cell.resize(new_size, Image.LANCZOS)
        canvas = Image.new("RGBA", size, (0, 0, 0, 0))
        canvas.paste(cell, ((size[0] - new_size[0]) // 2, (size[1] - new_size[1]) // 2))
        path = os.path.join(output, f"{index + 1:02d}.png")
        canvas.save(path)
        paths.append(path)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default=DEFAULT_SOURCE,
                        help=f"元画像(4x4グリッド)のパス。既定: {DEFAULT_SOURCE}")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                        help=f"出力フォルダ。既定: {DEFAULT_OUTPUT}")
    args = parser.parse_args()
    if not os.path.isfile(args.source):
        parser.error(f"元画像が見つかりません: {args.source}")
    for path in split(args.source, args.output):
        print(path)


if __name__ == "__main__":
    main()

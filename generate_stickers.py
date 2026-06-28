from io import BytesIO
import os
from pathlib import Path
import subprocess

import requests
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 370, 320
OUTPUT_DIR = Path("stickers")
CHICK_URL = "https://wanpug.com/illust/illust151.png"
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/ipafont-gothic/ipag.ttf",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
]

STICKER_TEXTS = [
    "おはよう",
    "おやすみ",
    "何してた？",
    "愛してる",
    "休憩だよ",
    "素敵な夢をみてね",
    "夢で逢えますように",
    "素敵な一日を",
    "無理しないで",
    "会えてうれしかったよ",
    "幸せだよ",
    "待っててね",
    "終わったよ",
    "いま出発",
    "お疲れさまでした",
    "ぎゅーして",
]


def download_chick_image() -> Image.Image:
    """ひよこ画像をダウンロードしてPIL Imageで返す。"""
    response = requests.get(CHICK_URL, timeout=30)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGBA")


def ensure_japanese_font() -> None:
    """Google Colab環境で日本語フォントを自動インストールする。"""
    noto_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    if not os.path.exists(noto_path):
        try:
            subprocess.run(
                ["apt-get", "install", "-y", "-q", "fonts-noto-cjk"],
                capture_output=True,
                timeout=120,
                check=False,
            )
        except Exception:
            pass


def load_font(size: int) -> ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def create_sticker(index: int, text: str, chick_img: Image.Image) -> None:
    """1枚分のスタンプを生成して保存する。"""
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 0))

    chick_area_height = HEIGHT - 85
    chick_area_width = WIDTH - 20

    chick_copy = chick_img.copy()
    chick_copy.thumbnail((chick_area_width, chick_area_height), Image.LANCZOS)

    x_offset = (WIDTH - chick_copy.width) // 2
    y_offset = (chick_area_height - chick_copy.height) // 2 + 10
    canvas.paste(chick_copy, (x_offset, y_offset), chick_copy)

    draw = ImageDraw.Draw(canvas)
    max_width = WIDTH - 20
    size = 42

    while size > 18:
        font = load_font(size)
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=3)
        if (bbox[2] - bbox[0]) <= max_width:
            break
        size -= 2

    font = load_font(size)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=3)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (WIDTH - text_w) // 2
    text_y = HEIGHT - 80 + (80 - text_h) // 2

    draw.text(
        (text_x, text_y),
        text,
        font=font,
        fill=(92, 61, 46, 255),
        stroke_width=4,
        stroke_fill=(255, 255, 255, 255),
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    canvas.save(OUTPUT_DIR / f"sticker_{index:02d}.png", "PNG")


def main() -> None:
    ensure_japanese_font()
    print("ひよこ画像をダウンロード中...")
    chick_img = download_chick_image()
    print("スタンプ生成中...")
    for i, text in enumerate(STICKER_TEXTS, start=1):
        create_sticker(i, text, chick_img)
        print(f"sticker_{i:02d}.png 生成完了")
    print(f"{len(STICKER_TEXTS)}枚のスタンプを {OUTPUT_DIR}/ に生成しました。")


if __name__ == "__main__":
    main()

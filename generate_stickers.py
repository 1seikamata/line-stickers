from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 370, 320
OUTPUT_DIR = Path("stickers")

STICKER_TEXTS = [
    "おはよう ☀️",
    "おやすみ 🌙",
    "何してた？",
    "愛してる 💕",
    "休憩だよ ☕",
    "素敵な夢をみてね 🌟",
    "夢で逢えますように 💫",
    "素敵な一日を過ごせますように 🌈",
    "無理しないで 🍀",
    "会えてうれしかったよ 😊",
    "幸せだよ 💛",
    "待っててね ⏳",
    "終わったよ 🎉",
    "いま出発 🚀",
    "お疲れさまでした 🌸",
    "ぎゅーして 🤗",
]

# 各スタンプのひよこ配置と表情（1羽/2羽、ポーズ違い）
STICKER_SCENES = [
    [(130, 180, "normal", "right")],
    [(130, 185, "sleepy", "right")],
    [(110, 180, "normal", "right"), (210, 180, "normal", "left")],
    [(110, 180, "heart", "right"), (210, 180, "heart", "left")],
    [(130, 180, "smile", "right")],
    [(130, 185, "sleepy", "right")],
    [(110, 185, "sleepy", "right"), (210, 185, "sleepy", "left")],
    [(110, 180, "smile", "right"), (210, 180, "smile", "left")],
    [(130, 180, "smile", "right")],
    [(110, 180, "wink", "right"), (210, 180, "smile", "left")],
    [(110, 180, "smile", "right"), (210, 180, "smile", "left")],
    [(130, 180, "normal", "right")],
    [(130, 180, "wink", "right")],
    [(130, 180, "normal", "right")],
    [(130, 180, "smile", "right")],
    [(110, 185, "smile", "right"), (210, 185, "smile", "left")],
]


def load_font(size: int) -> ImageFont.ImageFont:
    """日本語フォントを優先し、見つからない場合はPillowデフォルトへフォールバックする。"""
    candidates = [
        "NotoSansJP-Regular.otf",
        "NotoSansJP-Regular.ttf",
        "IPAexGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/ipafont-gothic/ipag.ttf",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
    ]
    for font_path in candidates:
        try:
            return ImageFont.truetype(font_path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_chick(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    expression: str = "normal",
    facing: str = "right",
) -> None:
    """図形だけでかわいいひよこを描く。"""
    body_color = (255, 236, 120, 255)
    body_shadow = (247, 216, 95, 255)
    blush = (255, 171, 204, 230)
    beak = (255, 170, 110, 255)
    eye = (56, 45, 63, 255)

    # 体と頭
    draw.ellipse((x - 48, y - 44, x + 48, y + 54), fill=body_shadow)
    draw.ellipse((x - 50, y - 46, x + 50, y + 52), fill=body_color)
    draw.ellipse((x - 34, y - 90, x + 34, y - 22), fill=body_color)

    # 羽（向きを変えてポーズの差分を作る）
    if facing == "right":
        draw.ellipse((x - 58, y - 18, x - 16, y + 20), fill=body_shadow)
        draw.ellipse((x + 8, y - 6, x + 44, y + 24), fill=body_shadow)
    else:
        draw.ellipse((x - 44, y - 6, x - 8, y + 24), fill=body_shadow)
        draw.ellipse((x + 16, y - 18, x + 58, y + 20), fill=body_shadow)

    # 足
    draw.line((x - 15, y + 52, x - 15, y + 66), fill=beak, width=4)
    draw.line((x + 15, y + 52, x + 15, y + 66), fill=beak, width=4)

    # 目
    left_eye = (x - 12, y - 58)
    right_eye = (x + 12, y - 58)
    if expression == "sleepy":
        draw.arc((left_eye[0] - 7, left_eye[1] - 2, left_eye[0] + 7, left_eye[1] + 8), 200, 340, fill=eye, width=3)
        draw.arc((right_eye[0] - 7, right_eye[1] - 2, right_eye[0] + 7, right_eye[1] + 8), 200, 340, fill=eye, width=3)
    elif expression == "wink":
        draw.ellipse((left_eye[0] - 3, left_eye[1] - 3, left_eye[0] + 3, left_eye[1] + 3), fill=eye)
        draw.line((right_eye[0] - 6, right_eye[1], right_eye[0] + 6, right_eye[1]), fill=eye, width=3)
    elif expression == "heart":
        draw.text((left_eye[0] - 8, left_eye[1] - 10), "❤", fill=(255, 102, 160, 255), font=load_font(16))
        draw.text((right_eye[0] - 8, right_eye[1] - 10), "❤", fill=(255, 102, 160, 255), font=load_font(16))
    else:
        draw.ellipse((left_eye[0] - 3, left_eye[1] - 3, left_eye[0] + 3, left_eye[1] + 3), fill=eye)
        draw.ellipse((right_eye[0] - 3, right_eye[1] - 3, right_eye[0] + 3, right_eye[1] + 3), fill=eye)

    # くちばしとほっぺ
    draw.polygon([(x - 7, y - 42), (x + 7, y - 42), (x, y - 32)], fill=beak)
    draw.ellipse((x - 30, y - 42, x - 20, y - 32), fill=blush)
    draw.ellipse((x + 20, y - 42, x + 30, y - 32), fill=blush)

    # 笑顔の口
    if expression == "smile":
        draw.arc((x - 10, y - 36, x + 10, y - 24), 20, 160, fill=(206, 110, 120, 255), width=2)


def draw_text_with_outline(draw: ImageDraw.ImageDraw, text: str) -> None:
    """下部にテキストを配置し、見やすいように縁取りする。"""
    max_width = WIDTH - 24
    size = 40
    font = load_font(size)

    # 文字列幅に合わせてフォントサイズを自動調整
    while size > 16:
        font = load_font(size)
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=3)
        if (bbox[2] - bbox[0]) <= max_width:
            break
        size -= 2

    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=3)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (WIDTH - text_w) // 2
    y = HEIGHT - text_h - 14

    draw.text(
        (x, y),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=4,
        stroke_fill=(181, 130, 215, 255),
    )


def create_sticker(index: int, text: str, scene: list[Tuple[int, int, str, str]]) -> None:
    """1枚分のスタンプを生成して保存する。"""
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # パステル調の装飾を薄く入れて華やかにする
    accents = [
        (55, 50, 26, (255, 224, 240, 150)),
        (320, 70, 20, (218, 230, 255, 140)),
        (70, 130, 16, (236, 226, 255, 135)),
    ]
    for ax, ay, r, color in accents:
        draw.ellipse((ax - r, ay - r, ax + r, ay + r), fill=color)

    for x, y, expression, facing in scene:
        draw_chick(draw, x, y, expression, facing)

    draw_text_with_outline(draw, text)

    OUTPUT_DIR.mkdir(exist_ok=True)
    image.save(OUTPUT_DIR / f"sticker_{index:02d}.png", "PNG")


def main() -> None:
    """16枚のスタンプを一括生成する。"""
    for i, (text, scene) in enumerate(zip(STICKER_TEXTS, STICKER_SCENES), start=1):
        create_sticker(i, text, scene)
    print(f"{len(STICKER_TEXTS)}枚のスタンプを {OUTPUT_DIR}/ に生成しました。")


if __name__ == "__main__":
    main()

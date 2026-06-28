"""見本画像に寄せたフラットなひよこLINEスタンプ生成スクリプト。"""

import math
import os
import re
import subprocess
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

# 画像サイズ（LINEスタンプ標準）
WIDTH, HEIGHT = 370, 320
OUTPUT_DIR = Path("stickers")

# スタンプテキスト一覧（16枚）
STICKER_TEXTS = [
    "おはよう ☀️",          # 01
    "おやすみ 🌙",           # 02
    "何してた？",             # 03
    "愛してる 💕",           # 04
    "休憩だよ ☕",           # 05
    "素敵な夢をみてね 🌟",    # 06
    "夢で逢えますように 💫",   # 07
    "素敵な一日を 🌈",       # 08
    "無理しないで 🍀",       # 09
    "会えてうれしかったよ 😊", # 10
    "幸せだよ 💛",           # 11
    "待っててね ⏳",          # 12
    "終わったよ 🎉",          # 13
    "いま出発 🚀",            # 14
    "お疲れさまでした 🌸",    # 15
    "ぎゅーして 🤗",          # 16
]

# 各スタンプのシーン定義: [(x, y, 表情, 向き), ...]
# 表情: normal / smile / sleepy / surprised / heart / wink / sparkle / blush
# 向き: right（右向き）/ left（左向き）
STICKER_SCENES = [
    [(185, 155, "smile",     "right")],              # 01 おはよう ☀️
    [(185, 155, "sleepy",    "right")],              # 02 おやすみ 🌙
    [(185, 155, "surprised", "right")],              # 03 何してた？
    [(115, 160, "heart",     "right"),               # 04 愛してる 💕（向き合い）
     (255, 160, "heart",     "left")],
    [(185, 155, "smile",     "right")],              # 05 休憩だよ ☕
    [(185, 155, "sleepy",    "right")],              # 06 素敵な夢をみてね 🌟
    [(115, 160, "smile",     "right"),               # 07 夢で逢えますように 💫（寄り添い）
     (255, 160, "smile",     "left")],
    [(185, 155, "sparkle",   "right")],              # 08 素敵な一日を 🌈
    [(185, 155, "blush",     "right")],              # 09 無理しないで 🍀
    [(115, 160, "smile",     "right"),               # 10 会えてうれしかったよ 😊（寄り添い）
     (255, 160, "smile",     "left")],
    [(115, 160, "heart",     "right"),               # 11 幸せだよ 💛（ハートあり）
     (255, 160, "heart",     "left")],
    [(185, 155, "wink",      "right")],              # 12 待っててね ⏳
    [(185, 155, "surprised", "right")],              # 13 終わったよ 🎉
    [(185, 155, "normal",    "right")],              # 14 いま出発 🚀
    [(185, 155, "blush",     "right")],              # 15 お疲れさまでした 🌸
    [(125, 160, "heart",     "right"),               # 16 ぎゅーして 🤗（くっついている）
     (245, 160, "heart",     "left")],
]

# 2羽の間にハートを浮かべるシーンの番号（0-indexed）
HEART_SCENES = {3, 10, 15}  # スタンプ04番, 11番, 16番

DEFAULT_FONT_TEXT_FALLBACKS = {
    "おはよう": "Good morning",
    "おやすみ": "Good night",
    "何してた？": "What were you doing?",
    "愛してる": "Love you",
    "休憩だよ": "Break time",
    "素敵な夢をみてね": "Sweet dreams",
    "夢で逢えますように": "See you in my dreams",
    "素敵な一日を": "Have a nice day",
    "無理しないで": "Take it easy",
    "会えてうれしかったよ": "Happy to see you",
    "幸せだよ": "I'm happy",
    "待っててね": "Wait for me",
    "終わったよ": "Done!",
    "いま出発": "Leaving now",
    "お疲れさまでした": "Good job",
    "ぎゅーして": "Hug me",
}

_font_warning_shown = False
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansJP-Regular.ttf",
    "/usr/share/fonts/truetype/ipafont-gothic/ipag.ttf",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
    "NotoSansJP-Regular.otf",
    "NotoSansJP-Regular.ttf",
]


def ensure_japanese_font() -> None:
    """Google Colab環境で日本語フォントを自動インストールする。"""
    if any(os.path.exists(font_path) for font_path in FONT_CANDIDATES):
        return

    try:
        result = subprocess.run(
            ["apt-get", "install", "-y", "-q", "fonts-noto-cjk"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if result.returncode == 0 and any(os.path.exists(font_path) for font_path in FONT_CANDIDATES):
            print("日本語フォントをインストールしました。")
    except Exception:
        pass


ensure_japanese_font()


def load_font(size: int, warn_if_default: bool = True) -> tuple[ImageFont.ImageFont, bool]:
    """日本語フォントを優先し、見つからない場合はPillowデフォルトへフォールバックする。"""
    for font_path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(font_path, size=size), False
        except (OSError, IOError):
            continue
    global _font_warning_shown
    if warn_if_default and not _font_warning_shown:
        print("警告: 日本語フォントが見つかりません。デフォルトフォントを使用します。")
        _font_warning_shown = True
    return ImageFont.load_default(), True


def strip_emoji(text: str) -> str:
    """絵文字などの装飾文字を除去し、日本語テキストを優先して残す。"""
    return re.sub(r"[^\u3000-\u9FFF\u30A0-\u30FF\u3040-\u309F\uFF00-\uFFEF\w\s？！。、]", "", text).strip()


def prepare_text_for_drawing(text: str, is_default_font: bool) -> str:
    """フォント状況に応じて描画用テキストを調整する。"""
    if not is_default_font:
        return text

    stripped_text = strip_emoji(text)
    return DEFAULT_FONT_TEXT_FALLBACKS.get(stripped_text, stripped_text)


def _draw_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: float, color: tuple) -> None:
    """5角星を描く（キラキラ目用）。"""
    points = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        r = size if i % 2 == 0 else size * 0.42
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=color)


def _draw_small_heart(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: float, color: tuple) -> None:
    """ハート形を描く（ハート目・2羽の間の浮かぶハート用）。
    パラメトリック方程式でなめらかなハートを生成する。
    """
    points = []
    scale = size / 16.0
    for t in range(0, 360, 4):
        rad = math.radians(t)
        hx = 16 * (math.sin(rad) ** 3)
        hy = -(13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad))
        points.append((cx + hx * scale, cy + hy * scale))
    draw.polygon(points, fill=color)


def draw_chick(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    expression: str = "normal",
    facing: str = "right",
    size_scale: float = 1.0,
) -> None:
    """見本画像に寄せた丸いひよこを描く。

    頭と体をほぼ同じ大きさにし、首が見えないくらい重ねる。
    x, y はひよこ全体の中心座標。
    """
    # === カラーパレット ===
    head_color = (255, 220, 50, 255)    # 明るい黄色の頭
    body_color = (255, 210, 30, 255)    # 少しだけ濃い黄色の体
    wing_color = (240, 180, 20, 255)    # 羽はさらに濃い黄色
    beak_color = (230, 140, 20, 255)    # くちばし・足はオレンジ
    cheek_color = (230, 150, 30, 200)   # ほっぺたはオレンジ系
    cheek_deep = (230, 150, 30, 230)    # 照れ顔だけ少し濃くする
    eye_color = (30, 30, 30, 255)       # シンプルな黒目
    heart_color = (255, 107, 157, 255)  # #FF6B9D ハート目

    # === パーツの基準座標 ===
    body_cx, body_cy = x, y + int(round(18 * size_scale))
    body_rx = max(28, int(round(45 * size_scale)))
    body_ry = max(27, int(round(43 * size_scale)))
    head_cx = x
    head_r = max(26, int(round(42 * size_scale)))
    overlap = max(12, int(round(20 * size_scale)))
    head_cy = body_cy - body_ry - head_r + overlap

    # === 描画順: 羽 → 体 → 頭 → 足 → 顔パーツ ===

    # --- 羽（体の左右にくっついた小さめの丸） ---
    wing_r = max(14, int(round(18 * size_scale)))
    wing_inset = max(5, int(round(8 * size_scale)))
    wing_y = body_cy - max(0, int(round(2 * size_scale)))
    draw.ellipse((body_cx - body_rx - wing_r + wing_inset, wing_y - wing_r,
                  body_cx - body_rx + wing_r + wing_inset, wing_y + wing_r), fill=wing_color)
    draw.ellipse((body_cx + body_rx - wing_r - wing_inset, wing_y - wing_r,
                  body_cx + body_rx + wing_r - wing_inset, wing_y + wing_r), fill=wing_color)

    # --- 体（頭と同じくらいの大きさで、少しだけ縦長） ---
    draw.ellipse((body_cx - body_rx, body_cy - body_ry,
                  body_cx + body_rx, body_cy + body_ry), fill=body_color)

    # --- 頭（大きな真円） ---
    draw.ellipse((head_cx - head_r, head_cy - head_r,
                  head_cx + head_r, head_cy + head_r), fill=head_color)

    # --- 足（極めて短く、体の下から少しだけ見せる） ---
    foot_top = body_cy + body_ry - 2
    foot_len = max(6, int(round(8 * size_scale)))
    foot_offset = max(9, int(round(12 * size_scale)))
    toe_dx = max(3, int(round(4 * size_scale)))
    toe_y = max(1, int(round(2 * size_scale)))
    foot_width = max(2, int(round(3 * size_scale)))
    for fx in (x - foot_offset, x + foot_offset):
        draw.line((fx, foot_top, fx, foot_top + foot_len), fill=beak_color, width=foot_width)
        draw.line((fx - toe_dx, foot_top + foot_len + toe_y, fx + toe_dx, foot_top + foot_len + toe_y),
                  fill=beak_color, width=max(1, foot_width - 1))

    # === 顔パーツの座標 ===
    beak_cx = head_cx
    beak_cy = head_cy + max(3, int(round(5 * size_scale)))
    eye_y = beak_cy - max(6, int(round(8 * size_scale)))
    eye_dx = max(8, int(round(11 * size_scale)))
    left_ex = beak_cx - eye_dx
    right_ex = beak_cx + eye_dx
    eye_r = max(4, int(round(5 * size_scale)))

    # === 目（表情によって変える） ===
    if expression == "smile":
        # にっこり目もシンプルな線でまとめる
        draw.arc((left_ex - 6, eye_y - 1, left_ex + 6, eye_y + 7), 15, 165, fill=eye_color, width=2)
        draw.arc((right_ex - 6, eye_y - 1, right_ex + 6, eye_y + 7), 15, 165, fill=eye_color, width=2)
    elif expression == "sleepy":
        # 眠そうな目は短い横線だけにする
        draw.line((left_ex - 5, eye_y, left_ex + 5, eye_y), fill=eye_color, width=2)
        draw.line((right_ex - 5, eye_y, right_ex + 5, eye_y), fill=eye_color, width=2)
    elif expression == "surprised":
        # びっくり目は少し大きめの黒丸
        big_eye_r = eye_r + max(1, int(round(2 * size_scale)))
        draw.ellipse((left_ex - big_eye_r, eye_y - big_eye_r, left_ex + big_eye_r, eye_y + big_eye_r), fill=eye_color)
        draw.ellipse((right_ex - big_eye_r, eye_y - big_eye_r, right_ex + big_eye_r, eye_y + big_eye_r), fill=eye_color)
    elif expression == "heart":
        # ハート目だけは演出として残す
        _draw_small_heart(draw, left_ex, eye_y, max(6, int(round(8 * size_scale))), heart_color)
        _draw_small_heart(draw, right_ex, eye_y, max(6, int(round(8 * size_scale))), heart_color)
    elif expression == "wink":
        # ウィンクは片目だけ点にする
        draw.ellipse((left_ex - eye_r, eye_y - eye_r, left_ex + eye_r, eye_y + eye_r), fill=eye_color)
        draw.arc((right_ex - 6, eye_y - 1, right_ex + 6, eye_y + 5), 200, 340, fill=eye_color, width=2)
    elif expression == "sparkle":
        # 見本優先で、キラキラ目も黒丸ベースに寄せる
        draw.ellipse((left_ex - eye_r, eye_y - eye_r, left_ex + eye_r, eye_y + eye_r), fill=eye_color)
        draw.ellipse((right_ex - eye_r, eye_y - eye_r, right_ex + eye_r, eye_y + eye_r), fill=eye_color)
    elif expression == "blush":
        # 照れ顔は普通の黒目で、ほっぺを強めにする
        draw.ellipse((left_ex - eye_r, eye_y - eye_r, left_ex + eye_r, eye_y + eye_r), fill=eye_color)
        draw.ellipse((right_ex - eye_r, eye_y - eye_r, right_ex + eye_r, eye_y + eye_r), fill=eye_color)
    else:
        # 基本は見本どおりの小さな黒丸
        draw.ellipse((left_ex - eye_r, eye_y - eye_r, left_ex + eye_r, eye_y + eye_r), fill=eye_color)
        draw.ellipse((right_ex - eye_r, eye_y - eye_r, right_ex + eye_r, eye_y + eye_r), fill=eye_color)

    # --- くちばし（横長のオレンジ楕円） ---
    beak_rx = max(7, int(round(10 * size_scale)))
    beak_ry = max(5, int(round(7 * size_scale)))
    draw.ellipse((beak_cx - beak_rx, beak_cy - beak_ry,
                  beak_cx + beak_rx, beak_cy + beak_ry), fill=beak_color)

    # --- ほっぺた（目の下外側にオレンジ色で置く） ---
    cheek_fill = cheek_deep if expression == "blush" else cheek_color
    cheek_y = eye_y + max(9, int(round(12 * size_scale)))
    cheek_rx = max(9, int(round(13 * size_scale)))
    cheek_ry = max(6, int(round(8 * size_scale)))
    cheek_gap = max(4, int(round(5 * size_scale)))
    draw.ellipse((left_ex - cheek_rx - cheek_gap, cheek_y - cheek_ry,
                  left_ex + cheek_rx - cheek_gap, cheek_y + cheek_ry), fill=cheek_fill)
    draw.ellipse((right_ex - cheek_rx + cheek_gap, cheek_y - cheek_ry,
                  right_ex + cheek_rx + cheek_gap, cheek_y + cheek_ry), fill=cheek_fill)


def draw_text_with_outline(draw: ImageDraw.ImageDraw, text: str) -> None:
    """画像下部1/4にテキストを配置し、白い縁取りと温かみのある茶色で描画する。"""
    max_width = WIDTH - 20
    size = 44   # 少し大きめのフォントサイズから開始

    # 文字幅に合わせてフォントサイズを自動縮小
    while size > 20:
        font, is_default_font = load_font(size, warn_if_default=False)
        draw_text = prepare_text_for_drawing(text, is_default_font)
        bbox = draw.textbbox((0, 0), draw_text, font=font, stroke_width=3)
        if (bbox[2] - bbox[0]) <= max_width:
            break
        size -= 2

    font, is_default_font = load_font(size)
    draw_text = prepare_text_for_drawing(text, is_default_font)
    bbox = draw.textbbox((0, 0), draw_text, font=font, stroke_width=3)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (WIDTH - text_w) // 2

    # テキストエリアは下部1/4（y=240〜320）の中央に縦配置
    text_area_top = HEIGHT * 3 // 4   # 240px
    text_y = text_area_top + (HEIGHT - text_area_top - text_h) // 2

    # 白い縁取り（アウトライン）＋ 温かみある茶色テキスト
    draw.text(
        (text_x, text_y),
        draw_text,
        font=font,
        fill=(92, 61, 46, 255),           # #5C3D2E 温かみのある茶色
        stroke_width=4,
        stroke_fill=(255, 255, 255, 255),  # 白い縁取り
    )


def create_sticker(index: int, text: str, scene: list[Tuple[int, int, str, str]]) -> None:
    """1枚分のスタンプを生成して保存する。"""
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # コーナーに薄いパステル円でふんわり装飾
    accents = [
        (50,  45, 22, (255, 240, 200, 110)),
        (325, 65, 18, (200, 235, 255, 100)),
        (65, 130, 15, (255, 220, 240,  95)),
    ]
    for ax, ay, r, color in accents:
        draw.ellipse((ax - r, ay - r, ax + r, ay + r), fill=color)

    # ひよこを描く
    size_scale = 0.75 if len(scene) == 2 else 1.0
    for x, y, expression, facing in scene:
        draw_chick(draw, x, y, expression, facing, size_scale=size_scale)

    # ハートシーンでは2羽の間にハートを浮かべる（index は1-based）
    if (index - 1) in HEART_SCENES and len(scene) == 2:
        mid_x = (scene[0][0] + scene[1][0]) // 2
        # ひよこの頭よりも少し上に浮かせる
        mid_y = min(scene[0][1], scene[1][1]) - 72
        _draw_small_heart(draw, mid_x, mid_y, 20, (255, 107, 157, 255))

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

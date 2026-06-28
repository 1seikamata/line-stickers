"""見本画像に忠実なフラットひよこLINEスタンプ生成スクリプト。"""

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

# 各スタンプのシーン定義: [(cx, cy, 表情, 向き), ...]
# 表情: normal / smile / sleepy / surprised / heart / wink / sparkle / blush
# 向き: right（右向き）/ left（左向き）
STICKER_SCENES = [
    [(185, 155, "smile",     "right")],              # 01 おはよう
    [(185, 155, "sleepy",    "right")],              # 02 おやすみ
    [(185, 155, "surprised", "right")],              # 03 何してた？
    [(110, 160, "heart",     "right"),               # 04 愛してる（向き合い）
     (260, 160, "heart",     "left")],
    [(185, 155, "smile",     "right")],              # 05 休憩だよ
    [(185, 155, "sleepy",    "right")],              # 06 素敵な夢をみてね
    [(115, 160, "smile",     "right"),               # 07 夢で逢えますように（寄り添い）
     (255, 160, "smile",     "left")],
    [(185, 155, "sparkle",   "right")],              # 08 素敵な一日を
    [(185, 155, "blush",     "right")],              # 09 無理しないで
    [(115, 160, "smile",     "right"),               # 10 会えてうれしかったよ（寄り添い）
     (255, 160, "smile",     "left")],
    [(110, 160, "heart",     "right"),               # 11 幸せだよ（ハートあり）
     (260, 160, "heart",     "left")],
    [(185, 155, "wink",      "right")],              # 12 待っててね
    [(185, 155, "surprised", "right")],              # 13 終わったよ
    [(185, 155, "normal",    "right")],              # 14 いま出発
    [(185, 155, "blush",     "right")],              # 15 お疲れさまでした
    [(120, 160, "heart",     "right"),               # 16 ぎゅーして（くっついている）
     (250, 160, "heart",     "left")],
]

# 2羽の間にハートを浮かべるシーンの番号（0-indexed）
HEART_SCENES = {3, 10, 15}  # スタンプ04番, 11番, 16番

_font_warning_shown = False
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/ipafont-gothic/ipag.ttf",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
]


def ensure_japanese_font() -> None:
    """Google Colab環境で日本語フォントを自動インストールする。"""
    noto_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    if not os.path.exists(noto_path):
        try:
            subprocess.run(
                ["apt-get", "install", "-y", "-q", "fonts-noto-cjk"],
                capture_output=True,
                timeout=120,
            )
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


def remove_emoji(text: str) -> str:
    """絵文字を除去し、日本語テキストのみを返す。"""
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text).strip()


def _draw_small_heart(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: float, color: tuple) -> None:
    """ハート形を描く（ハート目・2羽の間の浮かぶハート用）。
    パラメトリック方程式でなめらかなハートを生成する。
    """
    points = []
    s = size / 16.0
    for t in range(0, 360, 4):
        rad = math.radians(t)
        hx = 16 * (math.sin(rad) ** 3)
        hy = -(13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad))
        points.append((cx + hx * s, cy + hy * s))
    draw.polygon(points, fill=color)


def draw_chick(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    expression: str = "normal",
    facing: str = "right",
    scale: float = 1.0,
) -> None:
    """見本画像に忠実なフラットひよこを描く。

    cx, cy: ひよこ全体の中心座標
    scale: サイズ倍率（2羽の時は0.78など）
    頭が体より大きく、目が左右で高さが違う（左目が高い・右目が低い）。
    """
    # === カラーパレット（見本から正確に） ===
    head_color  = (255, 218,  33, 255)   # 明るい黄色（頭）
    body_color  = (245, 195,  20, 255)   # やや濃い黄色（体）
    wing_color  = (235, 175,  15, 255)   # さらに濃い黄色（羽）
    beak_color  = (220, 130,  10, 255)   # オレンジ（くちばし・足）
    cheek_color = (225, 155,  20, 200)   # オレンジ（ほっぺた）
    eye_color   = ( 20,  20,  20, 255)   # ほぼ黒（目）
    heart_color = (255, 100, 150, 255)   # ピンク（ハート目）

    # === パーツサイズ（scale=1.0 基準） ===
    r_head = int(48 * scale)
    r_body = int(38 * scale)
    r_wing = int(16 * scale)

    # === 座標計算 ===
    body_cx = cx
    body_cy = cy + int(10 * scale)
    head_cx = cx
    head_cy = body_cy - int(35 * scale)   # 体中心から35px上

    # === 描画順: 羽(後) → 体 → 頭 → 足 → 顔パーツ ===

    # --- 羽（体の下半分の左右に小さい丸） ---
    wing_y = body_cy + int(5 * scale)   # 体中心より少し下
    draw.ellipse((body_cx - r_body - r_wing + int(6 * scale),
                  wing_y - r_wing,
                  body_cx - r_body + r_wing + int(6 * scale),
                  wing_y + r_wing), fill=wing_color)
    draw.ellipse((body_cx + r_body - r_wing - int(6 * scale),
                  wing_y - r_wing,
                  body_cx + r_body + r_wing - int(6 * scale),
                  wing_y + r_wing), fill=wing_color)

    # --- 体 ---
    draw.ellipse((body_cx - r_body, body_cy - r_body,
                  body_cx + r_body, body_cy + r_body), fill=body_color)

    # --- 頭（体より大きい） ---
    draw.ellipse((head_cx - r_head, head_cy - r_head,
                  head_cx + r_head, head_cy + r_head), fill=head_color)

    # --- 足（超短い・体の底から少しだけ） ---
    foot_y_top = body_cy + r_body - int(4 * scale)
    foot_len   = int(8 * scale)
    foot_w     = max(2, int(3 * scale))
    for fx in (cx - int(12 * scale), cx + int(12 * scale)):
        draw.line((fx, foot_y_top, fx, foot_y_top + foot_len),
                  fill=beak_color, width=foot_w)
        draw.line((fx, foot_y_top + foot_len,
                   fx - int(5 * scale), foot_y_top + foot_len + int(3 * scale)),
                  fill=beak_color, width=max(1, foot_w - 1))
        draw.line((fx, foot_y_top + foot_len,
                   fx + int(5 * scale), foot_y_top + foot_len + int(3 * scale)),
                  fill=beak_color, width=max(1, foot_w - 1))

    # --- くちばし（目と目の真ん中・小さい横長楕円） ---
    beak_w      = int(14 * scale)
    beak_h      = int(9 * scale)
    beak_cy_pos = head_cy + int(8 * scale)
    draw.ellipse((head_cx - beak_w, beak_cy_pos - beak_h,
                  head_cx + beak_w, beak_cy_pos + beak_h), fill=beak_color)

    # --- 目の座標（左右で高さが違う） ---
    eye_r = max(4, int(5 * scale))
    # facing="right" のとき: 左目が高い・右目が低い
    # facing="left"  のとき: 右目が高い・左目が低い（左右反転）
    if facing == "right":
        left_eye_x  = head_cx - int(16 * scale)
        left_eye_y  = beak_cy_pos - int(12 * scale)   # 高い
        right_eye_x = head_cx + int(16 * scale)
        right_eye_y = beak_cy_pos - int(6 * scale)    # 低い
    else:
        left_eye_x  = head_cx - int(16 * scale)
        left_eye_y  = beak_cy_pos - int(6 * scale)    # 低い
        right_eye_x = head_cx + int(16 * scale)
        right_eye_y = beak_cy_pos - int(12 * scale)   # 高い

    # === 目（表情によって変える） ===
    arc_w = max(2, int(2 * scale))
    arc_d = max(6, int(6 * scale))   # 弧の直径の半分

    if expression == "smile":
        # 両目を下向きの弧に
        draw.arc((left_eye_x  - arc_d, left_eye_y  - 1,
                  left_eye_x  + arc_d, left_eye_y  + arc_d + 2), 15, 165, fill=eye_color, width=arc_w)
        draw.arc((right_eye_x - arc_d, right_eye_y - 1,
                  right_eye_x + arc_d, right_eye_y + arc_d + 2), 15, 165, fill=eye_color, width=arc_w)
    elif expression == "sleepy":
        # 両目を半目（横線）に
        draw.line((left_eye_x  - arc_d, left_eye_y,
                   left_eye_x  + arc_d, left_eye_y),  fill=eye_color, width=arc_w)
        draw.line((right_eye_x - arc_d, right_eye_y,
                   right_eye_x + arc_d, right_eye_y), fill=eye_color, width=arc_w)
    elif expression == "surprised":
        # 両目を大きい丸に
        big_r = eye_r + max(2, int(2 * scale))
        draw.ellipse((left_eye_x  - big_r, left_eye_y  - big_r,
                      left_eye_x  + big_r, left_eye_y  + big_r), fill=eye_color)
        draw.ellipse((right_eye_x - big_r, right_eye_y - big_r,
                      right_eye_x + big_r, right_eye_y + big_r), fill=eye_color)
    elif expression == "heart":
        # 両目をハート形に（ピンク）
        heart_size = max(6, int(8 * scale))
        _draw_small_heart(draw, left_eye_x,  left_eye_y,  heart_size, heart_color)
        _draw_small_heart(draw, right_eye_x, right_eye_y, heart_size, heart_color)
    elif expression == "wink":
        # 左目は黒丸・右目は弧（つぶり目）
        draw.ellipse((left_eye_x - eye_r, left_eye_y - eye_r,
                      left_eye_x + eye_r, left_eye_y + eye_r), fill=eye_color)
        draw.arc((right_eye_x - arc_d, right_eye_y - 1,
                  right_eye_x + arc_d, right_eye_y + arc_d + 2), 200, 340, fill=eye_color, width=arc_w)
    elif expression == "sparkle":
        # 両目を星形に
        star_size = max(5, int(6 * scale))
        _draw_star(draw, left_eye_x,  left_eye_y,  star_size, eye_color)
        _draw_star(draw, right_eye_x, right_eye_y, star_size, eye_color)
    elif expression == "blush":
        # 両目を細い弧に
        draw.arc((left_eye_x  - arc_d, left_eye_y  - 2,
                  left_eye_x  + arc_d, left_eye_y  + arc_d), 10, 170, fill=eye_color, width=arc_w)
        draw.arc((right_eye_x - arc_d, right_eye_y - 2,
                  right_eye_x + arc_d, right_eye_y + arc_d), 10, 170, fill=eye_color, width=arc_w)
    else:
        # normal: 左右非対称の黒丸
        draw.ellipse((left_eye_x  - eye_r, left_eye_y  - eye_r,
                      left_eye_x  + eye_r, left_eye_y  + eye_r), fill=eye_color)
        draw.ellipse((right_eye_x - eye_r, right_eye_y - eye_r,
                      right_eye_x + eye_r, right_eye_y + eye_r), fill=eye_color)

    # --- ほっぺた（オレンジ・目の外側下） ---
    cheek_w = int(13 * scale)
    cheek_h = int(10 * scale)
    cheek_y = left_eye_y + int(14 * scale)
    draw.ellipse((left_eye_x  - cheek_w, cheek_y - cheek_h,
                  left_eye_x  + cheek_w, cheek_y + cheek_h), fill=cheek_color)
    draw.ellipse((right_eye_x - cheek_w, cheek_y - cheek_h,
                  right_eye_x + cheek_w, cheek_y + cheek_h), fill=cheek_color)


def _draw_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: float, color: tuple) -> None:
    """5角星を描く（キラキラ目用）。"""
    points = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        r = size if i % 2 == 0 else size * 0.42
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=color)


def draw_text_with_outline(draw: ImageDraw.ImageDraw, text: str) -> None:
    """画像下部1/4にテキストを配置し、白い縁取りと温かみのある茶色で描画する。"""
    # 絵文字を除去して日本語部分のみ使用
    draw_text = remove_emoji(text)
    max_width = WIDTH - 20
    size = 44   # フォントサイズから開始

    # 文字幅に合わせてフォントサイズを自動縮小
    while size > 20:
        font, _ = load_font(size, warn_if_default=False)
        bbox = draw.textbbox((0, 0), draw_text, font=font, stroke_width=3)
        if (bbox[2] - bbox[0]) <= max_width:
            break
        size -= 2

    font, _ = load_font(size)
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

    # ひよこを描く（2羽の場合はscale=0.78）
    scale = 0.78 if len(scene) == 2 else 1.0
    for x, y, expression, facing in scene:
        draw_chick(draw, x, y, expression, facing, scale=scale)

    # ハートシーンでは2羽の間にハートを浮かべる（index は1-based）
    if (index - 1) in HEART_SCENES and len(scene) == 2:
        mid_x = (scene[0][0] + scene[1][0]) // 2
        # ひよこの頭よりも少し上に浮かせる
        mid_y = min(scene[0][1], scene[1][1]) - 72
        _draw_small_heart(draw, mid_x, mid_y, 20, (255, 100, 150, 255))

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

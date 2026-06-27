"""サンリオ風・ぷっくりまるまる系ひよこLINEスタンプ生成スクリプト。"""

import math
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
    [(185, 148, "smile",     "right")],              # 01 おはよう ☀️
    [(185, 148, "sleepy",    "right")],              # 02 おやすみ 🌙
    [(185, 148, "surprised", "right")],              # 03 何してた？
    [(120, 158, "heart",     "right"),               # 04 愛してる 💕（向き合い）
     (250, 158, "heart",     "left")],
    [(185, 148, "smile",     "right")],              # 05 休憩だよ ☕
    [(185, 148, "sleepy",    "right")],              # 06 素敵な夢をみてね 🌟
    [(125, 158, "smile",     "right"),               # 07 夢で逢えますように 💫（寄り添い）
     (245, 158, "smile",     "left")],
    [(185, 148, "sparkle",   "right")],              # 08 素敵な一日を 🌈
    [(185, 148, "blush",     "right")],              # 09 無理しないで 🍀
    [(125, 158, "smile",     "right"),               # 10 会えてうれしかったよ 😊（寄り添い）
     (245, 158, "smile",     "left")],
    [(120, 158, "heart",     "right"),               # 11 幸せだよ 💛（ハートあり）
     (250, 158, "heart",     "left")],
    [(185, 148, "wink",      "right")],              # 12 待っててね ⏳
    [(185, 148, "surprised", "right")],              # 13 終わったよ 🎉
    [(185, 148, "normal",    "right")],              # 14 いま出発 🚀
    [(185, 148, "blush",     "right")],              # 15 お疲れさまでした 🌸
    [(135, 158, "heart",     "right"),               # 16 ぎゅーして 🤗（くっついている）
     (235, 158, "heart",     "left")],
]

# 2羽の間にハートを浮かべるシーンの番号（0-indexed）
HEART_SCENES = {3, 10, 15}  # スタンプ04番, 11番, 16番


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
) -> None:
    """サンリオ風・ぷっくりまるまる系ひよこを描く。

    頭：体 = 1：1 のコンパクトな丸々デザイン。
    頭と体が重なり合い、首が見えないプロポーションにする。
    x, y はひよこ全体の中心座標。
    """
    # === カラーパレット ===
    head_color = (255, 229, 102, 255)   # #FFE566 頭（明るいパステルイエロー）
    body_color = (255, 215,   0, 255)   # #FFD700 体
    wing_color = (230, 185,   0, 255)   # 翼（体より少し濃い黄色）
    beak_color = (255, 140,   0, 255)   # #FF8C00 くちばし・足
    blush_color = (255, 183, 197, 200)  # #FFB7C5 ほっぺた（通常）
    blush_deep  = (255, 130, 155, 220)  # ほっぺた（照れ顔は濃いめ）
    eye_color   = ( 44,  44,  44, 255)  # #2C2C2C 目
    heart_color = (255, 107, 157, 255)  # #FF6B9D ハート目
    white       = (255, 255, 255, 255)  # ハイライト

    # === パーツの基準座標 ===
    body_cx, body_cy = x, y + 18   # 体の中心
    body_r = 42                    # 体の半径
    head_cx, head_cy = x, y - 32   # 頭の中心（体と重なるよう配置）
    head_r = 40                    # 頭の半径

    # === 描画順: 羽 → 体 → 頭 → 足 → アホ毛 → 顔パーツ ===

    # --- 羽（体の両サイドに小さめ楕円・体の約1/3サイズ） ---
    wing_rx, wing_ry = 13, 16   # 羽の半径（横, 縦）
    if facing == "right":
        # 右向き: 左羽を少し前方に出し、右羽を少し後方に
        draw.ellipse((body_cx - body_r - wing_rx + 4, body_cy - wing_ry,
                      body_cx - body_r + wing_rx + 4, body_cy + wing_ry), fill=wing_color)
        draw.ellipse((body_cx + body_r - wing_rx - 4, body_cy - wing_ry + 4,
                      body_cx + body_r + wing_rx - 4, body_cy + wing_ry + 4), fill=wing_color)
    else:
        # 左向き: 左右反転
        draw.ellipse((body_cx - body_r - wing_rx + 4, body_cy - wing_ry + 4,
                      body_cx - body_r + wing_rx + 4, body_cy + wing_ry + 4), fill=wing_color)
        draw.ellipse((body_cx + body_r - wing_rx - 4, body_cy - wing_ry,
                      body_cx + body_r + wing_rx - 4, body_cy + wing_ry), fill=wing_color)

    # --- 体（黄色い丸・羽の上に重ねて翼が両サイドから覗く） ---
    draw.ellipse((body_cx - body_r, body_cy - body_r,
                  body_cx + body_r, body_cy + body_r), fill=body_color)

    # --- 頭（明るめ黄色い丸・体と重なることで首を隠す） ---
    draw.ellipse((head_cx - head_r, head_cy - head_r,
                  head_cx + head_r, head_cy + head_r), fill=head_color)

    # --- 足（短くてかわいいオレンジ色・指付き） ---
    foot_top = body_cy + body_r - 6   # 体の底部付近から
    foot_len = 16                     # 足の長さ（体高の約1/4）
    for fx in (x - 15, x + 15):
        draw.line((fx, foot_top, fx, foot_top + foot_len), fill=beak_color, width=4)
        draw.line((fx, foot_top + foot_len, fx - 7, foot_top + foot_len + 5),
                  fill=beak_color, width=3)
        draw.line((fx, foot_top + foot_len, fx + 7, foot_top + foot_len + 5),
                  fill=beak_color, width=3)

    # --- アホ毛（頭頂部のぴょんと立った小さな突起） ---
    ahoge_base = head_cy - head_r   # 頭の一番上
    draw.ellipse((x + 2, ahoge_base - 14, x + 10, ahoge_base + 4), fill=head_color)

    # === 顔パーツの座標 ===
    eye_y   = head_cy - 8    # 目のY座標（頭中心より少し上）
    left_ex = head_cx - 13   # 左目のX座標
    right_ex = head_cx + 13  # 右目のX座標

    # === 目（表情によって変える） ===
    if expression == "smile":
        # にっこり: 下向き弧（目を細めた笑顔）
        draw.arc((left_ex  - 7, eye_y - 3, left_ex  + 7, eye_y + 7), 10, 170, fill=eye_color, width=3)
        draw.arc((right_ex - 7, eye_y - 3, right_ex + 7, eye_y + 7), 10, 170, fill=eye_color, width=3)
    elif expression == "sleepy":
        # 眠そうな目: 半目（下弧 + 上まぶた線）
        draw.arc((left_ex  - 7, eye_y - 5, left_ex  + 7, eye_y + 5), 185, 355, fill=eye_color, width=3)
        draw.line((left_ex  - 7, eye_y, left_ex  + 7, eye_y), fill=eye_color, width=2)
        draw.arc((right_ex - 7, eye_y - 5, right_ex + 7, eye_y + 5), 185, 355, fill=eye_color, width=3)
        draw.line((right_ex - 7, eye_y, right_ex + 7, eye_y), fill=eye_color, width=2)
    elif expression == "surprised":
        # びっくり目: 大きな丸目（ハイライト付き）
        draw.ellipse((left_ex  - 8, eye_y - 8, left_ex  + 8, eye_y + 8), fill=eye_color)
        draw.ellipse((left_ex  - 3, eye_y - 3, left_ex  + 3, eye_y + 3), fill=white)
        draw.ellipse((right_ex - 8, eye_y - 8, right_ex + 8, eye_y + 8), fill=eye_color)
        draw.ellipse((right_ex - 3, eye_y - 3, right_ex + 3, eye_y + 3), fill=white)
    elif expression == "heart":
        # ハート目: 小さなハート形
        _draw_small_heart(draw, left_ex,  eye_y, 8, heart_color)
        _draw_small_heart(draw, right_ex, eye_y, 8, heart_color)
    elif expression == "wink":
        # ウィンク: 左目は普通の丸目、右目は横弧（つぶった目）
        draw.ellipse((left_ex - 5, eye_y - 5, left_ex + 5, eye_y + 5), fill=eye_color)
        draw.ellipse((left_ex - 2, eye_y - 2, left_ex + 2, eye_y + 2), fill=white)
        draw.arc((right_ex - 7, eye_y - 2, right_ex + 7, eye_y + 6), 195, 345, fill=eye_color, width=3)
    elif expression == "sparkle":
        # キラキラ目: 星型
        _draw_star(draw, left_ex,  eye_y, 8, eye_color)
        _draw_star(draw, right_ex, eye_y, 8, eye_color)
    elif expression == "blush":
        # 照れ顔: にっこり目（細め）
        draw.arc((left_ex  - 6, eye_y - 2, left_ex  + 6, eye_y + 6), 10, 170, fill=eye_color, width=3)
        draw.arc((right_ex - 6, eye_y - 2, right_ex + 6, eye_y + 6), 10, 170, fill=eye_color, width=3)
    else:
        # normal: 普通の丸い目（ハイライト付き）
        draw.ellipse((left_ex  - 5, eye_y - 5, left_ex  + 5, eye_y + 5), fill=eye_color)
        draw.ellipse((left_ex  - 2, eye_y - 2, left_ex  + 2, eye_y + 2), fill=white)
        draw.ellipse((right_ex - 5, eye_y - 5, right_ex + 5, eye_y + 5), fill=eye_color)
        draw.ellipse((right_ex - 2, eye_y - 2, right_ex + 2, eye_y + 2), fill=white)

    # --- くちばし（小さいオレンジの三角形） ---
    beak_y = head_cy + 12
    draw.polygon([
        (x - 5, beak_y - 4),
        (x + 5, beak_y - 4),
        (x,     beak_y + 6),
    ], fill=beak_color)

    # --- ほっぺた（目の下にピンクの楕円） ---
    cheek_col = blush_deep if expression == "blush" else blush_color
    cheek_y = eye_y + 14
    draw.ellipse((left_ex  - 11, cheek_y - 6, left_ex  + 11, cheek_y + 6), fill=cheek_col)
    draw.ellipse((right_ex - 11, cheek_y - 6, right_ex + 11, cheek_y + 6), fill=cheek_col)


def draw_text_with_outline(draw: ImageDraw.ImageDraw, text: str) -> None:
    """画像下部1/4にテキストを配置し、白い縁取りと温かみのある茶色で描画する。"""
    max_width = WIDTH - 20
    size = 44   # 少し大きめのフォントサイズから開始

    # 文字幅に合わせてフォントサイズを自動縮小
    while size > 20:
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

    # テキストエリアは下部1/4（y=240〜320）の中央に縦配置
    text_area_top = HEIGHT * 3 // 4   # 240px
    text_y = text_area_top + (HEIGHT - text_area_top - text_h) // 2

    # 白い縁取り（アウトライン）＋ 温かみある茶色テキスト
    draw.text(
        (text_x, text_y),
        text,
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
    for x, y, expression, facing in scene:
        draw_chick(draw, x, y, expression, facing)

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

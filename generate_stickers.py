import argparse
from dataclasses import dataclass
from io import BytesIO
import math
import os
from pathlib import Path
import random
import subprocess

import requests
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

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


@dataclass
class AnimationConfig:
    """動くスタンプの設定（LINE仕様: 5〜20フレーム、ループ1〜4回、最大4秒）。"""

    frames: int = 12
    fps: int = 10
    speed: float = 1.0
    hearts: int = 4
    stars: int = 4
    loop: int = 2

    def validate(self) -> None:
        if not 5 <= self.frames <= 20:
            raise ValueError("frames は 5〜20 で指定してください")
        if self.fps < 1 or self.speed <= 0:
            raise ValueError("fps と speed は正の値にしてください")
        if not 1 <= self.loop <= 4:
            raise ValueError("loop は 1〜4 で指定してください")
        if self.hearts < 0 or self.stars < 0:
            raise ValueError("hearts と stars は 0 以上にしてください")
        if self.frames / self.fps * self.loop > 4:
            raise ValueError("総再生時間が4秒を超えています")


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


def render_chick(chick_img: Image.Image) -> Image.Image:
    """ひよこだけを透過キャンバスに配置した画像を返す。"""
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 0))

    chick_area_height = HEIGHT - 85
    chick_area_width = WIDTH - 20

    chick_copy = chick_img.copy()
    chick_copy.thumbnail((chick_area_width, chick_area_height), Image.LANCZOS)

    x_offset = (WIDTH - chick_copy.width) // 2
    y_offset = (chick_area_height - chick_copy.height) // 2 + 10
    canvas.paste(chick_copy, (x_offset, y_offset), chick_copy)
    return canvas


def draw_text(canvas: Image.Image, text: str) -> None:
    """キャンバス下部に縁取り付きテキストを描画する。"""
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



def create_sticker(index: int, text: str, chick_img: Image.Image) -> None:
    """1枚分のスタンプを生成して保存する。"""
    canvas = render_chick(chick_img)
    draw_text(canvas, text)
    OUTPUT_DIR.mkdir(exist_ok=True)
    canvas.save(OUTPUT_DIR / f"sticker_{index:02d}.png", "PNG")


HEART_COLORS = [(255, 105, 150, 255), (255, 150, 180, 255), (240, 70, 120, 255)]
STAR_COLORS = [(255, 215, 60, 255), (255, 240, 130, 255)]


def heart_polygon(cx: float, cy: float, size: float) -> list:
    pts = []
    for i in range(48):
        t = 2 * math.pi * i / 48
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * size / 32, cy - y * size / 32))
    return pts


def star_polygon(cx: float, cy: float, size: float, rotation: float) -> list:
    pts = []
    for i in range(10):
        r = size / 2 if i % 2 == 0 else size / 4.5
        a = rotation + math.pi * i / 5 - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def make_particles(config: AnimationConfig, seed: int) -> list:
    """パーティクル（ハート/星）の初期パラメータを決める。"""
    rng = random.Random(seed)
    particles = []
    for kind, count in (("heart", config.hearts), ("star", config.stars)):
        for _ in range(count):
            side = rng.choice([-1, 1])
            particles.append(
                {
                    "kind": kind,
                    "x": WIDTH / 2 + side * rng.uniform(95, 170),
                    "y": rng.uniform(25, HEIGHT - 110),
                    "size": rng.uniform(22, 40),
                    "phase": rng.uniform(0, 1),
                    "color": rng.choice(HEART_COLORS if kind == "heart" else STAR_COLORS),
                }
            )
    return particles


def render_frame(
    frame: int,
    config: AnimationConfig,
    chick_img: Image.Image,
    text: str,
    particles: list,
) -> Image.Image:
    """アニメーションの1フレームを描画する。"""
    # 1ループが frames 枚で綺麗に繋がるよう、位相は整数サイクルにする
    cycles = max(1, round(config.speed))
    t = frame / config.frames * cycles

    sway = math.sin(2 * math.pi * t)
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 0))
    chick = render_chick(chick_img)
    chick = chick.rotate(sway * 3, resample=Image.BICUBIC, center=(WIDTH / 2, HEIGHT - 85))
    layer.alpha_composite(chick, (round(sway * 4), round(math.sin(4 * math.pi * t) * 2)))

    draw = ImageDraw.Draw(layer)
    for p in particles:
        phase = (t + p["phase"]) % 1.0
        wave = math.sin(2 * math.pi * phase)
        if p["kind"] == "heart":
            size = p["size"] * (1 + 0.2 * wave)
            cx = p["x"] + 6 * math.sin(2 * math.pi * phase + 1)
            cy = p["y"] - 12 * wave
            draw.polygon(heart_polygon(cx, cy, size), fill=p["color"])
        else:
            blink = 0.55 + 0.45 * math.sin(4 * math.pi * phase)
            size = p["size"] * (0.7 + 0.3 * blink)
            color = p["color"][:3] + (round(255 * blink),)
            sparkle = Image.new("RGBA", layer.size, (0, 0, 0, 0))
            ImageDraw.Draw(sparkle).polygon(
                star_polygon(p["x"] + 8 * wave, p["y"] - 8 * wave, size, 2 * math.pi * phase / 4),
                fill=color,
            )
            layer.alpha_composite(sparkle)

    draw_text(layer, text)
    return layer


def create_animated_sticker(
    index: int, text: str, chick_img: Image.Image, config: AnimationConfig
) -> None:
    """1枚分の動くスタンプ(APNG)を生成して保存する。"""
    config.validate()
    particles = make_particles(config, seed=index)
    frames = [render_frame(i, config, chick_img, text, particles) for i in range(config.frames)]

    info = PngInfo()
    info.add_text("Title", f"animated_sticker_{index:02d}")
    info.add_text(
        "Animation",
        f"frames={config.frames};fps={config.fps};speed={config.speed};"
        f"hearts={config.hearts};stars={config.stars};loop={config.loop}",
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    frames[0].save(
        OUTPUT_DIR / f"animated_sticker_{index:02d}.png",
        "PNG",
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / config.fps),
        loop=config.loop,
        disposal=1,
        pnginfo=info,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LINEスタンプ生成")
    parser.add_argument("--static-only", action="store_true", help="静止画のみ生成")
    parser.add_argument("--animated-only", action="store_true", help="動くスタンプのみ生成")
    parser.add_argument("--frames", type=int, default=12, help="フレーム数(5-20)")
    parser.add_argument("--fps", type=int, default=10, help="フレームレート")
    parser.add_argument("--speed", type=float, default=1.0, help="アニメーション速度(1周期の回数)")
    parser.add_argument("--hearts", type=int, default=4, help="ハートの数")
    parser.add_argument("--stars", type=int, default=4, help="星の数")
    parser.add_argument("--loop", type=int, default=2, help="ループ回数(1-4)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = AnimationConfig(args.frames, args.fps, args.speed, args.hearts, args.stars, args.loop)
    config.validate()
    ensure_japanese_font()
    print("ひよこ画像をダウンロード中...")
    chick_img = download_chick_image()
    print("スタンプ生成中...")
    for i, text in enumerate(STICKER_TEXTS, start=1):
        if not args.animated_only:
            create_sticker(i, text, chick_img)
            print(f"sticker_{i:02d}.png 生成完了")
        if not args.static_only:
            create_animated_sticker(i, text, chick_img, config)
            print(f"animated_sticker_{i:02d}.png 生成完了")
    print(f"{len(STICKER_TEXTS)}枚のスタンプを {OUTPUT_DIR}/ に生成しました。")


if __name__ == "__main__":
    main()

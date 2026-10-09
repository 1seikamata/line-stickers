# LINEスタンプ生成スクリプト（ひよこ）

## スタンプの概要
Python（Pillow + requests）で、フリー素材のひよこ画像をダウンロードし、LINE公式スタンプサイズ（370×320px）のPNG画像を16枚まとめて生成します。  
ベース画像は `https://wanpug.com/illust/illust151.html` のひよこ素材を使用し、各スタンプでは下部に日本語テキストのみを追加します。背景は透過です。

## 必要な環境
- Python 3.x
- Pillow
- requests

## インストール方法
```bash
pip install -r requirements.txt
```

## 実行方法
```bash
python generate_stickers.py
```

## 生成されるファイル
実行後に `stickers/` フォルダが作成され、以下の16ファイルが生成されます。

- `stickers/sticker_01.png`
- `stickers/sticker_02.png`
- `stickers/sticker_03.png`
- `stickers/sticker_04.png`
- `stickers/sticker_05.png`
- `stickers/sticker_06.png`
- `stickers/sticker_07.png`
- `stickers/sticker_08.png`
- `stickers/sticker_09.png`
- `stickers/sticker_10.png`
- `stickers/sticker_11.png`
- `stickers/sticker_12.png`
- `stickers/sticker_13.png`
- `stickers/sticker_14.png`
- `stickers/sticker_15.png`
- `stickers/sticker_16.png`

## 動くスタンプ（APNG）
`python generate_stickers.py` は静止画に加えて、LINEの動くスタンプ用APNGも `stickers/animated_sticker_01.png`〜`animated_sticker_16.png` として生成します（Pillowのみ使用、追加ライブラリ不要）。
ひよこのゆらゆら動き、ハートの浮遊・拡大縮小、星の点滅・移動を各スタンプ12フレームで描画し、フレーム数・FPS・ループ回数などをPNGのメタデータ（`Animation`テキスト）にも記録します。

```bash
python generate_stickers.py --animated-only --frames 12 --fps 10 --speed 1 --hearts 4 --stars 4 --loop 2
```

| オプション | 既定値 | 説明 |
|---|---|---|
| `--static-only` / `--animated-only` | - | 静止画のみ / 動くスタンプのみ生成 |
| `--frames` | 12 | フレーム数（5〜20） |
| `--fps` | 10 | フレームレート |
| `--speed` | 1.0 | アニメーション速度（1ループ内の動きの周期数。整数に丸められます） |
| `--hearts` / `--stars` | 4 / 4 | ハート・星の数 |
| `--loop` | 2 | ループ回数（1〜4） |

LINEの仕様に合わせ、総再生時間（フレーム数 ÷ FPS × ループ回数）は4秒以内にしてください。

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

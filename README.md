# LINEスタンプ生成スクリプト（ひよこカップル）

## スタンプの概要
Python（Pillow）で、LINE公式スタンプサイズ（370×320px）のPNG画像を16枚まとめて生成します。  
キャラクターは黄色いかわいいひよこで、1羽または2羽の構図、ウィンク・ハート目・眠そうな目などの表情差分を入れています。背景は透過です。

## 必要な環境
- Python 3.x
- Pillow

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

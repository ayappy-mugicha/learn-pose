# 姿勢推定システム（Pose Estimation）の準備と動かし方

※このシステムはwindows11実行想定です。
## 前提
* VScodeがインストールされてること
* VScodeにpythonがインストールされていること

## 前準備
エクスプローラから、ダウンロードしたファイルにアクセスします。

フォルダーを開いたら、左クリックを押します。

![ターミナル左クリック](./images/image-1.png)
「ターミナルで開く」をクリック
![ターミナルの画面](./images/image-2.png)
ユーザーネームのあとに`\learn-pose-main`と表示されていたら準備完了です

## 1. 仮想環境（専用の作業部屋）を作る
[仮想環境とは](https://qiita.com/yasu_qita/items/197c94b2ad3003233407)

まずは、他のプログラムと設定が混ざらないように、システム専用の「部屋」を作る。
ターミナルを開いて、以下のコマンドを実行。

```bash
python -m venv venv
```

## 2.仮想環境に入りましょう。

仮想環境に入るためのコマンドは以下のとおりです。

```cmd
# コマンドプロンプトの場合
venv\Scripts\activate
```

``` powershell
# powershell の場合
venv\Scripts\activate.ps1
```

```bash
# linux or mac
source venv/bin/activate
```
仮想環境に入るとこのような表示になると思います。
![ターミナルの画面](./images/image-2.png)

## 3.必要なライブラリをインストールする

すでに、必要なライブラリをメモしてある`required.txt`というのを実行します。

```bash
pip install -r required.txt
```

これで最低限の準備は完了しました。

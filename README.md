# シラバス・時間割取得スクリプト

時間割とシラバスを加工してjsonに変換するためのスクリプトです。

## 環境構築

```bash
$ docker-compose build
```

## 設定ファイル

### config.yml

シラバスと時間割の全体的な設定ファイルです。
基本は触らなくても良いですが、以下でimportするファイルのパスとexportするファイルのパスを指定できます。
シラバスと時間割それぞれ指定可能です。

```yml
timetable:
  import_path: "files/xxx.xlsx"
  export_path: "files/xxx.json"
```

```yml
syllabus:
  import_path: "files/xxx.pdf"
  export_path: "tmp/xxx.json"
```

### bbox.csv

シラバスでPDFを取得するときに参照する座標が書かれています。座標を修正する必要が出たとき以外、触らなくて良いです。

| params | s-x1 | s-y1 | s-x2 | s-y2 | m-page-num | m-x1 | m-y1 | m-x2 | m-y2 |
|--------|------|------|------|------|------------|------|------|------|------|
| キー名 | x1座標(単体ページの場合) | y1座標(単体ページの場合) | x2座標(単体ページの場合) | y2座標(単体ページの場合) | ページ番号 | x1座標(単体ページの場合) | y1座標(単体ページの場合) | x2座標(単体ページの場合) | y2座標(単体ページの場合) 

## 実行

```bash
$ docker-compose up
```
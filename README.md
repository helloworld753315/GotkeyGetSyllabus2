# シラバス・時間割取得スクリプト

時間割とシラバスを加工してjsonに変換するためのスクリプトです。
2024年からシラバスがPDFをやめてwebサイトになったので、最新バージョンのスクリプトの使い方を記載します。
2023年までのスクリプトの説明は[こちら](docs/2023.md)。

## 環境構築

```bash
$ docker-compose build
```

## 設定ファイル

### config.yml

シラバスと時間割の全体的な設定ファイルです。
基本は触らなくても良いです。

時間割は、importするファイルのパスとexportするファイルのパスを指定できます。

```yml
timetable:
  import_path: "files/xxx.xlsx"
  export_path: "files/xxx.json"
```

シラバスは、インポートするシラバスの科目群ページを`urls`に指定します。

```yml
syllabus:
  urls: 
    - "https://www2.okiu.ac.jp/syllabus/2024/syllabus_%E4%BA%BA%E9%96%93%E6%96%87%E5%8C%96%E7%A7%91%E7%9B%AE%E7%BE%A4/8002_.html"
    - "https://www2.okiu.ac.jp/syllabus/2024/syllabus_%E7%A4%BE%E4%BC%9A%E7%94%9F%E6%B4%BB%E7%A7%91%E7%9B%AE%E7%BE%A4/8004_.html"
```

## 実行

```bash
$ docker-compose up
```

## ファイルの出力先。

実行すると、`app/tmp/out`内にjsonファイルが出力されます。

## キャッシュについて

繰り返し大学ページにアクセスして負荷をかけないようにするため、`app/.cache`というディレクトリにキャッシュを保存しています。
初回のみDLするようにしているため、もし情報が古かったり問題が起きた場合等はディレクトリの中身を一度消してみてください。
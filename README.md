# まどかAI観測所

AIニュースをカテゴリ別に眺めるための、GitHub Pages向けのシンプルなダッシュボードです。

現在はローカルで完成イメージを確認しやすいように、`news.json` にサンプルニュースを多めに入れています。将来的には GitHub Actions から `scripts/fetch_news.py` を実行して、RSS由来のニュースへ更新できます。

## カテゴリ

- AI全般
- 医療AI
- 医療ライター
- 医療イラスト
- 画像生成AI
- 動画生成AI
- 中国AI
- AI規制・著作権

## ファイル構成

- `index.html`: サイト本体。`news.json` を読み込み、カテゴリ別にニュースカードを表示します。
- `news.json`: 表示用ニュースデータ。タイトル、出典、日付、カテゴリ、1行メモ、リンクを持ちます。
- `scripts/fetch_news.py`: RSSを取得し、カテゴリ判定して `news.json` を生成するPythonスクリプトです。
- `.github/workflows/fetch-news.yml`: GitHub Actionsで定期的にニュース取得を実行する設定です。

## ローカルで確認する

ブラウザで `index.html` を開くと画面を確認できます。

ブラウザの制限で `news.json` の読み込みに失敗する場合は、簡易サーバーを起動してください。

```bash
python -m http.server 8000
```

その後、以下を開きます。

```text
http://localhost:8000/
```

## RSS更新に必要なもの

- Python 3
- `feedparser`

```bash
python -m pip install feedparser
python scripts/fetch_news.py
```

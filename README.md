# 📈 株式AI分析ツール

日本株・米国株向けのAI支援分析ツールです。ローソク足チャート、豊富なテクニカル指標、財務指標、AIによる分析レポート、ニュース駆動の銘柄スクリーニングをStreamlitの複数ページアプリとして提供します。デフォルトは日本語UIで、英語表示への切り替えにも対応しています。

公開デモ: https://kabusearch.streamlit.app/

## 主な機能

- **銘柄分析（メインページ）**
  - ローソク足チャート + MA/ボリンジャーバンド/一目均衡表/VWAPなどのオーバーレイ
  - RSI・MACD・ADX・OBVなどのテクニカル指標
  - 指標ごとの買い/売り/中立シグナルと総合判定
  - PER・PBR・ROEなどの財務指標、業績推移、業績予想、大株主一覧
  - 日本株は信用取引（買い残・売り残・倍率）の推移も表示
  - 日経平均 / S&P 500 との比較チャートと超過リターン
  - AIモデル（ローカルOllama or Gemini API）による自然文の分析レポート
- **注目銘柄スクリーニング（ページ）**
  - 日経・Yahoo!ニュースの経済見出しをAIが分析し、翌営業日以降に注目すべき銘柄を抽出
- **ウォッチリスト一覧（ページ）**
  - 登録銘柄の現在値・値動き・価格チャート（1日〜2年の期間切り替え）をまとめて表示
  - 銘柄ごとにメモを残せる
  - フォルダ（自分で名前を決められるグループ）で銘柄を整理
- **ウォッチリスト（サイドバー）**
  - 🌐 公開リスト（訪問者全員が見られる）
  - 🏘️ コミュニティリスト（名前+合言葉で保護、仲間内で共有）
  - 👤 個人リスト（名前+合言葉で保護）
  - 合言葉を忘れた場合は名前を指定して再設定可能
  - データはFirestoreに保存され、どこからアクセスしても永続化される

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数（`.env`）

```
GEMINI_API_KEY=あなたのGemini APIキー
GOOGLE_APPLICATION_CREDENTIALS=./firebase-key.json
```

- `GEMINI_API_KEY`: [Google AI Studio](https://aistudio.google.com/)で取得。ローカルにOllamaが無い/繋がらない場合、AI機能はGemini APIにフォールバックします。
- `GOOGLE_APPLICATION_CREDENTIALS`: Firestore用のGCPサービスアカウントキー（JSON）のパス。ウォッチリストの保存に使用します。Firebase Console →プロジェクトの設定→サービスアカウント から発行できます。

Streamlit Cloudなどにデプロイする場合は、`.env`の代わりにアプリのSecretsに`GEMINI_API_KEY`と`[firestore_credentials]`テーブル（サービスアカウントJSONの中身）を設定してください（`src/watchlist.py`が自動的にSecrets経由の認証情報を読み込みます）。

### 3. （任意）ローカルAIモデル

AI分析をローカルで動かす場合はOllamaが必要です。

```bash
ollama serve
ollama pull <モデル名>
```

Ollamaが起動していない/モデルが応答しない場合も、Gemini APIキーが設定されていればそちらにフォールバックします。

## 起動方法

```bash
streamlit run app.py --server.port 8501
```

Windowsでは `起動.bat` をダブルクリックすると、ポートの起動確認をした上でStreamlitを立ち上げ、ブラウザを自動で開きます。

テスト用の接続確認スクリプトも用意しています。

```bash
python test_gemini_connection.py       # Gemini APIの疎通確認
python test_firestore_connection.py    # Firestoreの疎通確認
```

## アーキテクチャ

Streamlitのファイルベース・マルチページ機能を使用しています。`app.py`がメインページ、`pages/`以下が追加ページとしてサイドバーに自動表示されます。ページ間で共有されるのは`st.session_state`のみです。

```
app.py                              # メインページ（銘柄分析）
pages/
  1_注目銘柄スクリーニング.py         # ニュースAIスクリーニング
  2_ウォッチリスト一覧.py             # ウォッチリストのダッシュボード
src/
  data_fetcher.py                   # yfinanceラッパー（株価・財務情報）
  technical_analysis.py             # テクニカル指標・シグナル計算（純関数）
  chart_builder.py                  # Plotlyチャート生成（純関数）
  ai_analyst.py                     # 銘柄分析用プロンプト生成・AIストリーミング
  stock_screener.py                 # スクリーニング用プロンプト生成・AIストリーミング
  gemini_client.py                  # Gemini APIクライアント
  news_fetcher.py                   # 日経・Yahoo!ニュースのスクレイピング/RSS取得
  watchlist.py                      # Firestoreベースのウォッチリスト永続化
  margin_fetcher.py / holder_fetcher.py / stock_search.py
  ui.py                             # 共通CSSテーマ
```

データフロー（メインページ）: `data_fetcher` → `technical_analysis.add_indicators` → `get_signals` / `get_summary_stats` → `chart_builder`（チャート）/ `ai_analyst`（AI分析）で描画。

## 技術スタック

Python / Streamlit / yfinance / Plotly / pandas / Google Cloud Firestore / Ollama / Google Gemini API / deep-translator / BeautifulSoup

## 注意事項

本ツールが提供する分析・シグナル・AIレポートは投資助言ではありません。投資判断は自己責任で行ってください。

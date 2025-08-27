# 勤怠管理システム - デプロイメントガイド

## 概要
FastAPI + JavaScript の勤怠管理システムのデプロイメント手順

## 必要な環境
- Python 3.11+
- Git
- Heroku CLI (Herokuにデプロイする場合)

## ファイル構成
```
attendance-tool/
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPIメインアプリケーション
│   │   ├── core/           # データベース、認証設定
│   │   ├── models/         # データベースモデル
│   │   ├── routers/        # APIルーター
│   │   └── schemas/        # Pydanticスキーマ
│   └── attendance.db       # SQLiteデータベース
├── frontend/
│   ├── index.html          # メインHTML
│   ├── styles.css          # CSS
│   └── js/
│       └── debug-app.js    # メインJavaScript
├── requirements.txt        # Python依存関係
├── Procfile               # Heroku設定
├── runtime.txt            # Python版本指定
└── .env.example           # 環境変数の例
```

## Herokuへのデプロイ手順

### 1. Herokuアカウント作成・CLI インストール
```bash
# Heroku CLI をインストール
# https://devcenter.heroku.com/articles/heroku-cli

# ログイン
heroku login
```

### 2. アプリケーション作成
```bash
# バックエンド用アプリケーション作成
heroku create your-attendance-backend

# フロントエンド用アプリケーション作成（静的サイト）
heroku create your-attendance-frontend
```

### 3. バックエンドデプロイ
```bash
# 環境変数設定
heroku config:set SECRET_KEY="your-secret-key-here" -a your-attendance-backend
heroku config:set ALLOWED_ORIGINS="https://your-attendance-frontend.herokuapp.com" -a your-attendance-backend

# バックエンドデプロイ
git subtree push --prefix=backend heroku-backend main

# または
cd backend
git init
heroku git:remote -a your-attendance-backend
git add .
git commit -m "Deploy backend"
git push heroku main
```

### 4. フロントエンドデプロイ
```bash
# 静的サイト用buildpack設定
heroku buildpacks:set https://github.com/heroku/heroku-buildpack-static -a your-attendance-frontend

# static.json作成（フロントエンドディレクトリ内）
echo '{"root": "."}' > frontend/static.json

# フロントエンドのAPI URLを更新
# frontend/js/debug-app.js の API_BASE_URL を本番URLに変更

# フロントエンドデプロイ
cd frontend
git init
heroku git:remote -a your-attendance-frontend
git add .
git commit -m "Deploy frontend"
git push heroku main
```

## その他のクラウドサービスへのデプロイ

### Netlify (フロントエンド)
1. Netlifyアカウント作成
2. GitHub連携でリポジトリ選択
3. ビルド設定: `frontend/` ディレクトリを指定
4. 環境変数でAPI URLを設定

### Railway (バックエンド)
1. Railwayアカウント作成
2. GitHub連携でリポジトリ選択
3. `backend/` ディレクトリを指定
4. 環境変数を設定

### Vercel (フロントエンド)
1. Vercelアカウント作成
2. GitHub連携でリポジトリ選択
3. `frontend/` ディレクトリを指定

## 環境変数の設定

### バックエンド
```
SECRET_KEY=強力なシークレットキー
ALLOWED_ORIGINS=フロントエンドのURL
PORT=8001
```

### フロントエンド
JavaScript内でAPI URLを環境に応じて設定:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' ? 
    'http://localhost:8001' : 
    'https://your-backend-app.herokuapp.com';
```

## データベース
- 開発環境: SQLite
- 本番環境: PostgreSQL推奨（Heroku Postgres等）

本番環境でPostgreSQLを使用する場合:
```bash
# Heroku Postgres addon追加
heroku addons:create heroku-postgresql:mini -a your-attendance-backend

# データベースURL自動設定
heroku config -a your-attendance-backend
```

## セキュリティ設定
1. 強力なSECRET_KEYを設定
2. CORS設定を本番URLに限定
3. HTTPS使用を強制

## トラブルシューティング
- ログ確認: `heroku logs --tail -a app-name`
- 環境変数確認: `heroku config -a app-name`
- データベース確認: `heroku pg:psql -a app-name`
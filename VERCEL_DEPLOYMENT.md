# Vercel デプロイメントガイド

## 概要
勤怠管理システムをVercelにデプロイする手順です。

## 前提条件
- Vercelアカウント（無料で作成可能）
- GitHubアカウント
- Node.js環境（Vercel CLIを使用する場合）

## デプロイ方法

### 方法1: Vercel CLI を使用（推奨）

1. **Vercel CLIをインストール**
```bash
npm i -g vercel
```

2. **プロジェクトディレクトリで実行**
```bash
cd attendance-tool
vercel
```

3. **プロンプトに従って設定**
- プロジェクト名を入力
- フレームワークの自動検出: Other
- ルートディレクトリ: ./
- ビルドコマンド: なし（Enter）
- 出力ディレクトリ: frontend

4. **環境変数の設定**
```bash
# Vercel ダッシュボードまたはCLIで設定
vercel env add SECRET_KEY
vercel env add ALLOWED_ORIGINS
```

環境変数の値：
- `SECRET_KEY`: 強力なシークレットキー（例: `your-secret-key-here-change-in-production`）
- `ALLOWED_ORIGINS`: フロントエンドのURL（例: `https://your-app.vercel.app`）

### 方法2: GitHub連携

1. **GitHubにプッシュ**
```bash
git add .
git commit -m "Add Vercel configuration"
git push origin main
```

2. **Vercelダッシュボードで設定**
- https://vercel.com/dashboard にアクセス
- "New Project" をクリック
- GitHubリポジトリを選択
- 設定を確認してデプロイ

## ファイル構成

```
attendance-tool/
├── api/
│   └── index.py           # Vercel用APIエントリーポイント
├── backend/
│   ├── app/
│   └── attendance.db
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── js/
│   │   └── debug-app.js
│   └── vercel.json       # フロントエンド用Vercel設定
├── vercel.json           # メインVercel設定
├── requirements.txt      # Python依存関係
└── .vercelignore        # デプロイ除外ファイル
```

## 設定ファイル説明

### `vercel.json`
- APIルーティング設定
- Python関数の設定
- バックエンドファイルのインクルード設定

### `api/index.py`
- FastAPIアプリケーションのエントリーポイント
- Vercel Serverless Functions用の設定

### `frontend/vercel.json`
- SPAルーティング設定
- キャッシュ設定

## デプロイ後の確認

1. **デプロイURL確認**
```bash
vercel ls
```

2. **ログ確認**
```bash
vercel logs
```

3. **環境変数確認**
```bash
vercel env ls
```

## アクセスURL

デプロイ後、以下のURLでアクセス可能：
- フロントエンド: `https://your-app.vercel.app`
- API: `https://your-app.vercel.app/api`

## トラブルシューティング

### APIが動作しない場合
1. 環境変数が正しく設定されているか確認
2. `api/index.py` が正しくデプロイされているか確認
3. Vercelのファンクションログを確認

### CORSエラーが発生する場合
1. `ALLOWED_ORIGINS` 環境変数を確認
2. フロントエンドのAPI URLが正しいか確認

### データベースエラーが発生する場合
- SQLiteファイルは読み取り専用になる可能性があります
- 本番環境では外部データベース（PostgreSQL等）の使用を推奨

## 本番環境での推奨設定

1. **外部データベース使用**
   - Supabase、PlanetScale、Neon等のデータベースサービス
   - 環境変数 `DATABASE_URL` で接続設定

2. **セキュリティ強化**
   - 強力な `SECRET_KEY` の使用
   - HTTPS強制
   - Rate limiting設定

3. **パフォーマンス最適化**
   - CDNキャッシュ設定
   - 画像最適化
   - コード分割

## 更新方法

```bash
# コード変更後
git add .
git commit -m "Update"
git push origin main

# または Vercel CLI で直接デプロイ
vercel --prod
```

## サポート

- Vercel ドキュメント: https://vercel.com/docs
- FastAPI ドキュメント: https://fastapi.tiangolo.com/
- 問題が発生した場合は GitHub Issues で報告してください
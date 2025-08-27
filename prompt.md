# 勤怠管理システム - 継続開発プロンプト

## システム概要
日本語対応の勤怠管理システム（FastAPI + Vanilla JavaScript）が完成し、現在稼働中です。

## 現在の状況
- **バックエンド**: http://localhost:8001 で稼働中（FastAPIサーバー）
- **フロントエンド**: http://localhost:3000 で稼働中（HTTPサーバー）
- **デバッグ版JavaScript**: `frontend/js/debug-app.js` を使用中
- **テストユーザー**: ユーザー名 `testuser`、パスワード `testpass`

## 技術スタック
### バックエンド
- **フレームワーク**: FastAPI
- **データベース**: SQLite
- **認証**: JWT (Bearer Token)
- **パスワードハッシュ化**: bcrypt
- **構成**: モジュラー構造
  - `backend/app/main.py` - メインアプリケーション
  - `backend/app/core/` - 設定、DB、セキュリティ
  - `backend/app/models/` - データベースモデル
  - `backend/app/routers/` - APIエンドポイント
  - `backend/app/schemas/` - Pydanticスキーマ
  - `backend/app/services/` - ユーティリティ関数

### フロントエンド
- **技術**: Vanilla JavaScript (ES6+)、HTML5、CSS3
- **現在使用中**: `frontend/js/debug-app.js` (シンプル版)
- **モジュール版**: `frontend/js/app.js` + modules/ (未使用)
- **UI**: レスポンシブデザイン、Font Awesome

## 主要機能
1. **ユーザー認証** - ログイン/ログアウト
2. **勤怠記録** - 出勤/退勤/休憩開始/休憩終了
3. **管理者機能** - ユーザー管理、勤怠修正
4. **修正申請** - ユーザーが申請、管理者が承認
5. **履歴表示** - 勤怠履歴、修正申請履歴

## 現在の実装状況
### 正常動作中
- ✅ ユーザーログイン/ログアウト
- ✅ 出勤/退勤/休憩の記録
- ✅ リアルタイム状態更新
- ✅ JWT認証とCORS設定

### 一部制限あり
- ⚠️ メモ機能は無効化（prompt削除済み）
- ⚠️ ESモジュール版は未使用（debug版使用中）

## ファイル構造
```
attendance-tool/
├── backend/
│   ├── main.py (旧版、未使用)
│   ├── app/
│   │   ├── main.py (現在使用中)
│   │   ├── core/ (設定、DB、認証)
│   │   ├── models/ (User, AttendanceRecord, CorrectionRequest)
│   │   ├── routers/ (auth, attendance, admin, corrections, reports)
│   │   ├── schemas/ (Pydantic)
│   │   └── services/ (ユーティリティ)
│   └── attendance.db (SQLiteデータベース)
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js.old (バックアップ)
│   ├── test.html (テスト用)
│   └── js/
│       ├── debug-app.js (現在使用中)
│       ├── app.js (ESモジュール版、未使用)
│       ├── config.js
│       ├── utils.js
│       └── modules/ (auth, attendance, correction, admin)
└── README.md
```

## データベーススキーマ
- **users**: id, username, email, hashed_password, full_name, is_admin, created_at
- **attendance_records**: id, user_id, date, clock_in, clock_out, break_start, break_end, notes, status, admin_log, created_at, updated_at
- **correction_requests**: id, user_id, attendance_record_id, requested_*, reason, status, admin_notes, approved_by, created_at, updated_at

## 起動方法
```bash
# バックエンド起動
cd backend
python -m app.main

# フロントエンド起動（別ターミナル）
cd frontend
python -m http.server 3000
```

## API仕様
- `POST /auth/login` - ログイン
- `POST /auth/register` - ユーザー登録  
- `GET /attendance/today` - 今日の勤怠状況
- `GET /attendance/` - 勤怠履歴
- `POST /attendance/` - 勤怠記録
- `GET /admin/users` - 全ユーザー取得（管理者のみ）
- `POST /admin/attendance/correct` - 直接修正（管理者のみ）
- `POST /correction-request/` - 修正申請作成
- `GET /correction-request/` - 自分の修正申請
- `GET /correction-request/admin/all` - 全修正申請（管理者のみ）
- `PUT /correction-request/{id}/approve` - 申請承認/拒否（管理者のみ）

## 既知の問題と改善点
1. **ESモジュール版の未完成** - 一部onclick属性が残存
2. **メモ機能の無効化** - promptダイアログを削除済み
3. **エラーハンドリング** - 一部alertが残存

## 継続開発のポイント
- デバッグ版で基本機能は完動
- ESモジュール版への移行は後回し可能
- UIの改善とユーザビリティ向上が次のステップ
- テスト環境としてlocalhost環境が整備済み

## 注意事項
- 現在はデバッグ版JavaScript使用中のため、モジュール版の修正は不要
- バックエンドは完全にリファクタリング済み
- データベースにはテストデータが蓄積済み
- Git履歴は保持されており、いつでも前のバージョンに戻せる

---
**状態**: 基本機能完動、継続開発準備完了  
**最終更新**: 2025-08-27  
**作業者**: Claude Code
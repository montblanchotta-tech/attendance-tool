@echo off
echo ========================================
echo 外部アクセス用サーバー起動（ngrok）
echo ========================================
echo.

REM ngrokが存在するか確認
where ngrok >nul 2>nul
if %errorlevel% neq 0 (
    echo エラー: ngrokがインストールされていません
    echo.
    echo ngrokをインストールしてください:
    echo 1. https://ngrok.com/download にアクセス
    echo 2. Windows版をダウンロード
    echo 3. ZIPを解凍してPATHに追加
    echo.
    pause
    exit /b
)

echo [1/2] 統合サーバーを起動中...
start cmd /k "python run.py"

echo.
echo 3秒待機中...
timeout /t 3 /nobreak > nul

echo.
echo [2/2] ngrokトンネルを作成中...
echo.
echo ========================================
echo 重要: ngrokウィンドウに表示される
echo       https://xxxx.ngrok.io 
echo       のURLを使用してアクセスしてください
echo ========================================
echo.

start cmd /k "ngrok http 8001"

echo.
echo ========================================
echo 起動完了！
echo.
echo ngrokウィンドウで以下を確認:
echo - Forwarding: https://xxxx.ngrok.io
echo.
echo このURLを他のデバイスで開いてください
echo ========================================
pause
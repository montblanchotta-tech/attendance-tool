@echo off
echo ========================================
echo 勤怠管理システム - ネットワーク起動
echo ========================================
echo.

REM ファイアウォールの警告が出た場合は「アクセスを許可」してください

REM IPアドレスを取得
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set IP=%%b
        goto :found
    )
)
:found

echo ローカルIPアドレス: %IP%
echo.
echo アクセスURL:
echo   同じPC: http://localhost:3000
echo   他のデバイス: http://%IP%:3000
echo.
echo APIサーバー:
echo   同じPC: http://localhost:8001
echo   他のデバイス: http://%IP%:8001
echo.
echo ========================================
echo.

REM バックエンドサーバー起動
echo [1/2] バックエンドサーバーを起動中...
start cmd /k "cd backend && python -m app.main"

REM 3秒待機
timeout /t 3 /nobreak > nul

REM フロントエンドサーバー起動
echo [2/2] フロントエンドサーバーを起動中...
start cmd /k "cd frontend && python -m http.server 3000 --bind 0.0.0.0"

echo.
echo ========================================
echo 起動完了！
echo.
echo ブラウザで以下のURLにアクセスしてください:
echo   http://%IP%:3000
echo.
echo 終了する場合は、開いたウィンドウをすべて閉じてください
echo ========================================
pause
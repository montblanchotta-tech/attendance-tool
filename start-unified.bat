@echo off
echo ========================================
echo 勤怠管理システム - 統合サーバー起動
echo ========================================
echo.

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
echo   同じPC: http://localhost:8001
echo   他のデバイス: http://%IP%:8001
echo.
echo ========================================
echo.

echo 統合サーバーを起動中...
echo （フロントエンドとAPIを同じポートで提供）
echo.

cd backend
python -m app.main

pause
@echo off
echo ========================================
echo ngrok簡単インストーラー
echo ========================================
echo.

echo ngrokをダウンロード中...
echo.

REM PowerShellでダウンロード
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'}"

if not exist ngrok.zip (
    echo ダウンロード失敗
    echo.
    echo 手動でダウンロードしてください:
    echo https://ngrok.com/download
    pause
    exit /b
)

echo.
echo 解凍中...
powershell -Command "Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force"

if exist ngrok.exe (
    echo.
    echo ========================================
    echo ngrokのインストール完了！
    echo ========================================
    echo.
    echo 次のステップ:
    echo 1. https://dashboard.ngrok.com/signup で無料アカウント作成
    echo 2. 認証トークンを取得
    echo 3. 以下のコマンドを実行:
    echo    ngrok config add-authtoken YOUR_TOKEN
    echo.
    echo その後、start-ngrok.bat を実行してください
    echo ========================================
) else (
    echo 解凍失敗
)

REM クリーンアップ
del ngrok.zip 2>nul

pause
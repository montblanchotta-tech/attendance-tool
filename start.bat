@echo off
echo 勤怠管理システムを起動しています...
echo.
echo バックエンドサーバーを起動中...
cd backend
start "Backend Server" cmd /k "python main.py"
echo.
echo フロントエンドを起動中...
cd ..\frontend
start "Frontend Server" cmd /k "python -m http.server 3000"
echo.
echo サーバーが起動しました！
echo バックエンド: http://localhost:8001
echo フロントエンド: http://localhost:3000
echo.
pause
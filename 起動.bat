@echo off
chcp 65001 > nul
cd /d %~dp0

:: すでに起動中か確認
netstat -ano | findstr ":8501 " > nul 2>&1
if %errorlevel% == 0 (
    echo [既に起動中] http://localhost:8501 を開きます...
    start http://localhost:8501
    exit /b
)

echo [起動中] Streamlit を起動しています...
start "" "C:\Users\GE00514\AppData\Local\Python\pythoncore-3.14-64\Scripts\streamlit.exe" run app.py --server.port 8501 --browser.gatherUsageStats false

echo [待機中] ブラウザを開くまで少々お待ちください...
powershell -Command "do { Start-Sleep -Milliseconds 500 } until ((Test-NetConnection localhost -Port 8501 -InformationLevel Quiet -WarningAction SilentlyContinue)); Write-Host '[完了] ブラウザを開きます'; Start-Process 'http://localhost:8501'"

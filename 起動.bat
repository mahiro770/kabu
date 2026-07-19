@echo off
chcp 65001 > nul
cd /d %~dp0

:: すでに起動中か確認
netstat -ano | findstr ":8501 " > nul 2>&1
if %errorlevel% == 0 (
    echo [既に起動中] 初めのページを開きます...
    start "" "%~dp0landing\home.html"
    exit /b
)

echo [起動中] Streamlit を起動しています...
start "" "C:\Users\GE00514\AppData\Local\Python\pythoncore-3.14-64\Scripts\streamlit.exe" run app.py --server.port 8501 --browser.gatherUsageStats false

echo [起動中] 初めのページを開きます...
start "" "%~dp0landing\home.html"

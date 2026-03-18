@echo off
chcp 65001 >nul
echo ==========================================
echo   GRID.DOMINION 本地服务器启动器
echo ==========================================
echo.
echo 正在启动服务器...
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请安装 Python 3.x
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 获取当前文件夹路径
set "WEB_DIR=%~dp0web"

REM 检查 web 文件夹是否存在
if not exist "%WEB_DIR%" (
    echo [错误] 未找到 web 文件夹
    echo 请确保此 bat 文件与 web 文件夹在同一目录
    pause
    exit /b 1
)

echo [1/3] Python 检测通过
echo [2/3] 找到 web 文件夹: %WEB_DIR%
echo [3/3] 正在启动服务器...
echo.
echo ==========================================
echo  服务器地址: http://localhost:8000
echo  按 Ctrl+C 停止服务器
echo ==========================================
echo.

REM 启动浏览器
timeout /t 1 /nobreak >nul
start http://localhost:8000

REM 启动 Python 服务器
cd /d "%WEB_DIR%"
python -m http.server 8000

pause
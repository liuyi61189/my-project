@echo off
chcp 65001 >nul
echo ========================================
echo   TestHub 一键部署
echo ========================================
echo.

REM 1. 构建前端
echo [1/3] 构建前端...
cd /d C:\TestHub\frontend
call npm run build
if %errorlevel% neq 0 (
    echo 前端构建失败！
    pause
    exit /b 1
)
echo 前端构建完成 ✓
echo.

REM 2. 重建 Docker 镜像
echo [2/3] 重建 Docker 镜像（可能需要几分钟）...
cd /d C:\TestHub
docker-compose build
if %errorlevel% neq 0 (
    echo 镜像构建失败！
    pause
    exit /b 1
)
echo 镜像构建完成 ✓
echo.

REM 3. 启动容器
echo [3/3] 启动容器...
docker-compose up -d
if %errorlevel% neq 0 (
    echo 容器启动失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo   部署完成！
echo   前端地址: http://localhost:8080
echo   后端地址: http://localhost:8000
echo ========================================
pause

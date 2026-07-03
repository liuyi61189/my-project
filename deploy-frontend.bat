@echo off
chcp 65001 >nul
echo ========================================
echo   TestHub 前端快速部署
echo ========================================
echo.

REM 1. 构建前端
echo [1/2] 构建前端...
cd /d C:\TestHub\frontend
call npm run build
if %errorlevel% neq 0 (
    echo 前端构建失败！
    pause
    exit /b 1
)
echo 前端构建完成 ✓
echo.

REM 2. 直接复制到容器
echo [2/2] 部署到容器...
docker cp C:\TestHub\frontend\dist\. testhub-frontend:\usr\share\nginx\html\
docker restart testhub-frontend

echo.
echo ========================================
echo   前端部署完成！
echo   访问: http://localhost:8080
echo ========================================
pause

@echo off
chcp 65001 >nul
echo ============================================
echo   游戏配表检索工具 - 一键打包脚本
echo ============================================
echo. 

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 安装/检查PyInstaller...
pip install pyinstaller -q

echo [2/3] 检查依赖包...
pip install pandas openpyxl msgpack -q

echo [3/3] 开始打包...
echo. 

REM 【优化】清理旧的打包文件前，先备份 .index 索引目录（如果存在）
REM 索引目录位于 dist/.index，打包时 dist 会被整个删除，导致索引丢失
if exist dist\.index (
    echo [备份] 检测到索引目录 dist\.index，正在备份到临时文件夹...
    xcopy /E /I /Q /Y /H dist\.index _index_backup_\.index >nul 2>&1
    echo [备份] 索引目录已备份
) else (
    echo [提示] 未检测到索引目录 dist\.index，跳过备份
)

REM 清理旧的打包文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

REM 执行打包（使用命令行参数方式，兼容Python 3.14+）
pyinstaller --onefile --windowed --name GameConfigSearcher --add-data "config.json;." --hidden-import pandas --hidden-import openpyxl --hidden-import pandas._libs --hidden-import pandas._libs.tslibs --hidden-import numpy --hidden-import msgpack --hidden-import msgpack._cmsgpack --hidden-import zlib gui_app.py

if exist dist\GameConfigSearcher.exe (
    echo.
    echo ============================================
    echo   ✅ 打包成功！
    echo   输出文件: dist\GameConfigSearcher.exe
    echo ============================================
    echo. 

    REM 【优化】恢复索引目录到 dist/.index
    if exist _index_backup_\.index (
        echo [恢复] 正在恢复索引目录到 dist\.index...
        xcopy /E /I /Q /Y /H _index_backup_\.index dist\.index >nul 2>&1
        rmdir /s /q _index_backup_
        echo [恢复] 索引目录已恢复，打包后索引数据不会丢失
    )

    echo 双击 dist\GameConfigSearcher.exe 即可运行
    echo. 
    explorer dist
) else (
    echo.
    echo ============================================
    echo   ❌ 打包失败，请检查错误信息
    echo ============================================
    
    REM 打包失败也要清理临时备份
    if exist _index_backup_ rmdir /s /q _index_backup_
)

pause
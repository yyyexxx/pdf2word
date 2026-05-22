@echo off
setlocal

echo ========================================
echo   PDF转WORD转换器 - Windows Build
echo ========================================

echo.
echo [1/3] 创建干净虚拟环境...
if exist .venv_build rmdir /s /q .venv_build
python -m venv .venv_build
call .venv_build\Scripts\activate.bat

echo [2/3] 安装依赖...
pip install -q PyMuPDF python-docx Pillow PySide6 pyinstaller

echo [3/3] PyInstaller 打包...
pyinstaller pdf2word.spec --noconfirm --clean

echo.
echo ========================================
echo   构建完成!
echo   便携版: dist\pdf2word.exe
echo ========================================

echo.
echo 如需生成安装包，安装 NSIS 后运行:
echo   winget install NSIS.NSIS
echo   makensis scripts\installer.nsi
echo.
pause

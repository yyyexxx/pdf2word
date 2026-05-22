#!/bin/bash
set -e

echo "========================================"
echo "  PDF转WORD转换器 - macOS Build"
echo "========================================"
echo ""

echo "[1/3] 创建干净虚拟环境..."
rm -rf .venv_build
python3 -m venv .venv_build
source .venv_build/bin/activate

echo "[2/3] 安装依赖..."
pip install -q PyMuPDF python-docx Pillow PySide6 pyinstaller

echo "[3/3] PyInstaller 打包..."
pyinstaller pdf2word.spec --noconfirm --clean

echo ""
echo "========================================"
echo "  构建完成!"
echo "  可执行文件: dist/pdf2word"
echo "========================================"
echo ""

# Ask about DMG creation
read -p "创建 DMG 安装包? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "[4/4] 创建 DMG..."
    mkdir -p dist/dmg
    cp -R dist/pdf2word dist/dmg/
    cp README.md dist/dmg/ 2>/dev/null || true

    # Create Applications folder symlink for drag-to-install
    ln -sf /Applications dist/dmg/Applications 2>/dev/null || true

    hdiutil create -volname "PDF转WORD" \
        -srcfolder dist/dmg \
        -ov -format UDZO \
        "dist/PDF转WORD转换器.dmg"

    rm -rf dist/dmg
    echo ""
    echo "DMG 安装包: dist/PDF转WORD转换器.dmg"
    echo ""
    echo "签名和公证请运行: bash scripts/sign_mac.sh"
fi

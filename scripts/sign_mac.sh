#!/bin/bash
# macOS 代码签名 + 公证脚本
# 使用前需设置环境变量或修改以下变量:
#   APPLE_ID=your@email.com
#   APPLE_TEAM_ID=你的团队ID (在 developer.apple.com 查看)
#   APP_PASSWORD=应用专用密码 (在 appleid.apple.com 生成)

set -e

APP_NAME="pdf2word"
APP_BUNDLE="dist/${APP_NAME}.app"
ENTITLEMENTS="scripts/entitlements.plist"

if [ ! -d "$APP_BUNDLE" ]; then
    echo "错误: 找不到 $APP_BUNDLE"
    echo "请先运行: pyinstaller --windowed --name $APP_NAME src/main.py"
    exit 1
fi

# 1. 签名所有 dylib 和 framework
echo "=== 签名内部文件 ==="
find "$APP_BUNDLE" -type f \( -name "*.dylib" -o -name "*.so" -o -name "Python" \) -print0 | while IFS= read -r -d '' f; do
    codesign --force --options runtime --timestamp --sign "Developer ID Application: ${APPLE_TEAM_ID}" "$f" 2>/dev/null || true
done

# 2. 签名 .app 包
echo "=== 签名 App Bundle ==="
codesign --force --options runtime --timestamp \
    --entitlements "$ENTITLEMENTS" \
    --sign "Developer ID Application: ${APPLE_TEAM_ID}" \
    "$APP_BUNDLE"

# 3. 创建 DMG
echo "=== 创建 DMG ==="
mkdir -p dist/dmg
cp -R "$APP_BUNDLE" dist/dmg/
hdiutil create -volname "$APP_NAME" -srcfolder dist/dmg -ov -format UDZO "dist/${APP_NAME}.dmg"

# 4. 公证
echo "=== 提交公证 ==="
xcrun notarytool submit "dist/${APP_NAME}.dmg" \
    --apple-id "$APPLE_ID" \
    --team-id "$APPLE_TEAM_ID" \
    --password "$APP_PASSWORD" \
    --wait

# 5. 装订票据
echo "=== 装订公证票据 ==="
xcrun stapler staple "dist/${APP_NAME}.dmg"

echo "=== 完成 ==="
echo "可分发的 DMG: dist/${APP_NAME}.dmg"

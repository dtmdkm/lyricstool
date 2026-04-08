#!/usr/bin/env bash
set -e

echo "============================================"
echo "  LyricsSRT Converter - macOS/Linux Build"
echo "============================================"

echo "[1/3] Cài đặt thư viện..."
pip install -r requirements.txt
pip install pyinstaller

echo "[2/3] Đang build ứng dụng..."
pyinstaller build.spec --noconfirm

echo "[3/3] Nén thành file ZIP..."
cd dist
zip -r ../LyricsSRTConverter-$(uname -s).zip LyricsSRTConverter
cd ..

echo ""
echo "============================================"
echo "  HOÀN THÀNH!"
echo "  Thư mục: dist/LyricsSRTConverter/"
echo "  ZIP:     LyricsSRTConverter-$(uname -s).zip"
echo "============================================"

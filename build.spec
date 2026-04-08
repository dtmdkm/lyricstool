# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — builds a single-folder distribution of LyricsSRTConverter.
Run:  pyinstaller build.spec --noconfirm
Output: dist/LyricsSRTConverter/
"""

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

datas = []
datas += collect_data_files("faster_whisper")
datas += collect_data_files("imageio_ffmpeg")
datas += collect_data_files("tokenizers")
datas += collect_data_files("ctranslate2")

binaries = []
binaries += collect_dynamic_libs("ctranslate2")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "faster_whisper",
        "ctranslate2",
        "imageio_ffmpeg",
        "tokenizers",
        "huggingface_hub",
        "huggingface_hub.file_download",
        "tqdm",
        "av",
        "numpy",
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["matplotlib", "tkinter", "PIL", "cv2"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LyricsSRTConverter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no terminal window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="LyricsSRTConverter",
)

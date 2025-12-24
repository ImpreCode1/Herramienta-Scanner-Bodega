# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/gui.py'],
    pathex=['src'],
    binaries=[
        ('runtime/tesseract/tesseract.exe', 'runtime/tesseract'),
        ('runtime/poppler/Library/bin', 'runtime/poppler/Library/bin'),
        ('runtime/zbar/bin/*', 'runtime/zbar/bin')
    ],
    datas=[
        ('runtime/tesseract/tessdata', 'runtime/tesseract/tessdata'),
        ('src/assets', 'src/assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ScannerBodega',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='src/assets/logo_impresistem.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='ScannerBodega',
)

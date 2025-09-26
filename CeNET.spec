# -*- mode: python -*-

block_cipher = None


def get_datas():
    from pathlib import Path

    base = Path(__file__).resolve().parent
    examples_dir = base / "examples"
    datas = [(str(base / "config.ini"), ".")]
    if examples_dir.exists():
        for item in examples_dir.iterdir():
            datas.append((str(item), f"examples/{item.name}"))
    return datas


a = Analysis(
    ['app/main.py'],
    pathex=['.'],
    binaries=[],
    datas=get_datas(),
    hiddenimports=['tkinter', 'pdfplumber', 'reportlab', 'pandas', 'requests'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CeNET',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='CeNET'
)

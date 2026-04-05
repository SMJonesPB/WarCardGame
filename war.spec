# war.spec — consolidated, clean, production-ready

block_cipher = None

import os
from PyInstaller.utils.hooks import collect_submodules

# Collect all modules inside engine/ and gui/
engine_modules = collect_submodules('engine')
gui_modules = collect_submodules('gui')

# Bundle card images + WinSparkle DLL
datas = [
    ('../Card Pictures', 'Card Pictures'),
]

binaries = [
    ('WinSparkle.dll', '.'),   # bundle updater DLL
]

a = Analysis(
    ['main.py'],               # ONLY build War.exe from main.py
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=engine_modules + gui_modules,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='War',                # final EXE name
    debug=False,
    strip=False,
    upx=True,
    console=False,
    #icon='war.ico',            # your icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='War',
)
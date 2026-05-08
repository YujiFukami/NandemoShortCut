# -*- mode: python ; coding: utf-8 -*-


main_analysis = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('NandemoShortcut.ico', '.')],
    hiddenimports=['comtypes', 'comtypes.client'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
main_pyz = PYZ(main_analysis.pure)

main_exe = EXE(
    main_pyz,
    main_analysis.scripts,
    main_analysis.binaries,
    main_analysis.datas,
    [],
    name='NandemoShortcut',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NandemoShortcut.ico',
)

launcher_analysis = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('NandemoShortcut.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
launcher_pyz = PYZ(launcher_analysis.pure)

launcher_exe = EXE(
    launcher_pyz,
    launcher_analysis.scripts,
    launcher_analysis.binaries,
    launcher_analysis.datas,
    [],
    name='NandemoShortcutLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NandemoShortcut.ico',
)

# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec para empaquetar DocumentaryAI Studio como ejecutable de escritorio.
#
#   pip install pyinstaller PySide6
#   pyinstaller app/studio/packaging/DocumentaryAI-Studio.spec
#
# Genera dist/DocumentaryAI Studio/DocumentaryAI Studio.exe (Windows) o el binario equivalente.
# Este .spec deja preparado el empaquetado; NO se construye en este sprint.

block_cipher = None

a = Analysis(
    ["../__main__.py"],                 # entrada: python -m app.studio
    pathex=["."],
    binaries=[],
    datas=[],                           # Studio no embebe knowledge/ ni output/ (viven en disco)
    hiddenimports=["app.studio.ui.app", "app.studio.ui.main_window"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["torch", "whisper"],      # el aprendizaje corre en un proceso aparte (learn_queue)
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="DocumentaryAI Studio",
    console=False,                      # aplicación de escritorio: sin ventana de consola
    disable_windowed_traceback=False,
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name="DocumentaryAI Studio")

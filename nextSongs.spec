# -*- mode: python -*-

block_cipher = None


a = Analysis(['nextSongs\\ui.py'],
             pathex=['E:\\nextSongs'],
             binaries=[],
             datas=[('nextSongs/icons/icon.png', 'icons')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='nextSongs',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='nextSongs\\icons\\icon.ico')

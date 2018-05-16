# -*- mode: python -*-

from sys import platform

if platform == 'darwin':
    icon_path = 'ui\images\icon.icns'
elif platform == 'linux':
    icon_path = 'ui\images\icon.png'
else:
    icon_path = 'ui\images\icon.ico'

block_cipher = None


a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[],
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
          name='WuxiaDownloader',
          debug=False,
          onefile=True,
          windowed=True,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon=icon_path )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='WuxiaDownloader')
app = BUNDLE(coll,
             name='WuxiaDownloader.app'
             icon=icon_path
             bundle_identifier = 'com.insopl.wuxiadownloader' )

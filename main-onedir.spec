# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Windows\\System32\\downlevel', 'C:\\Users\\john\\PycharmProjects\\WebControl'],
             binaries=[],
             datas=[('templates', 'templates'), ('firmware','firmware'), ('static', 'static'), ('tools', 'tools'),('defaultwebcontrol.json', '.')],
             hiddenimports=['flask', 'flask-misaka', 'clr', 'gevent', 'gevent-websocket', 'engineio.async_gevent', 'distro'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
          a.binaries,
          a.zipfiles,
          a.datas,
          strip=False,
          upx=True,
          name='main')

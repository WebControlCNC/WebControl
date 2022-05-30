# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['~/Documents/GitHub/WebControl'],
             binaries=[],
             datas=[('templates', 'templates'), ('firmware','firmware'), ('static', 'static'), ('tools', 'tools'), ('docs','docs'), ('defaultwebcontrol.json', '.')],
             hiddenimports=['flask', 'flask-misaka', 'clr', 'gevent', 'gevent-websocket', 'engineio.async_gevent', 'distro', 'markdown'],
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
          name='webcontrol',
          debug=False,
          strip=False,
          upx=True,
          console=True,
          icon = 'webcontrolicon_256px.ico' )
coll = COLLECT(exe,
          a.binaries,
          a.zipfiles,
          a.datas,
          strip=False,
          upx=True,
          name='main')


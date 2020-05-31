# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=['C:\\Windows\\System32\\downlevel', 'C:\\Users\\john\\PycharmProjects\\WebControl', 'C:\\Users\\jhoga\\Documents\\GitHub\\WebControl'],
             binaries=[],
             datas=[('templates', 'templates'), ('firmware','firmware'), ('static', 'static'), ('tools', 'tools'), ('docs', 'docs'), ('defaultwebcontrol.json', '.')],
             hiddenimports=['flask', 'flask-misaka', 'clr', 'gevent', 'gevent-websocket', 'engineio.async_gevent', 'psutil', 'distro', 'markdown', 'markdown.extensions.fenced_code'],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='webcontrol',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          icon = 'webcontrolicon_256px.ico')

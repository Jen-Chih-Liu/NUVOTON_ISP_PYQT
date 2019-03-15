# -*- mode: python -*-

block_cipher = None
binaries_a = [
   ('C:\\Windows\\SysWOW64\\libusb-1.0.dll', '.'),
]

a = Analysis(['pyisp.py'],
             pathex=['C:\\Users\\jcliu\\Documents\\Visual Studio 2013\\Projects\\pyusb\\pyusb'],
             binaries=binaries_a,
             datas=[],
             hiddenimports=['usb'],
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
          exclude_binaries=True,
          name='pyisp',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='pyisp')


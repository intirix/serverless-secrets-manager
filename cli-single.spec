# -*- mode: python -*-

block_cipher = None

import os, site
from distutils.sysconfig import get_python_lib
import glob

site_packages_dir = get_python_lib()
try:
	site_packages_dir = site.getsitepackages()[1]
except:
	pass


a = Analysis(['cli.py'],
             pathex=[os.getcwd()],
             binaries=[],
             datas=[],
             hiddenimports=['queue'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

a.binaries.append(('_scrypt', glob.glob(site_packages_dir+'/_scrypt*')[0], 'EXTENSION'))
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          [],
          a.zipfiles,
          a.datas,
          name='ServerLessSecretsManagerCLI',
          debug=False,
          strip=False,
          upx=True,
          console=True )

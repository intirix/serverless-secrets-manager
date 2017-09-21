# -*- mode: python -*-

block_cipher = None

import os, site
from distutils.sysconfig import get_python_lib

site_packages_dir = get_python_lib()
try:
        site_packages_dir = site.getsitepackages()[1]
except:
        pass
print("site_packages="+site_packages_dir)
qml_dir = os.path.join(site_packages_dir, 'PyQt5', 'Qt', 'qml')
print("qml_dir="+qml_dir)

added_files = [
    (os.path.join(qml_dir, 'QtQuick'), '_qml/QtQuick'),
    (os.path.join(qml_dir, 'QtQuick.2'), '_qml/QtQuick.2'),
]


a = Analysis(['ui.py'],
             pathex=['/home/jeff/Dev/ServerLessSecretManager'],
             binaries=[
                 (site_packages_dir+'/PyQt5/Qt/lib/libQt5Quick.so.5','.'),
                 (site_packages_dir+'/PyQt5/Qt/lib/libQt5Sql.so.5','.'),
                 (site_packages_dir+'/PyQt5/Qt/plugins/sqldrivers','qt5_plugins/sqldrivers'),
                 (site_packages_dir+'/PyQt5/Qt/plugins/egldeviceintegrations','qt5_plugins/egldeviceintegrations'),
                 (site_packages_dir+'/PyQt5/Qt/plugins/xcbglintegrations','qt5_plugins/xcbglintegrations')
             ],
             datas=added_files,
             hiddenimports=["queue"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
a.binaries.append(('_scrypt', '.contents_ui/lib/python3.5/site-packages/_scrypt.cpython-35m-x86_64-linux-gnu.so', 'EXTENSION'))

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='cpmqdir',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               Tree('ui',prefix='ui/'),
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='cpmqdir')

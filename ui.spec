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
print("site_packages="+site_packages_dir)


# Add all the system qml files
qml_dir = os.path.join(site_packages_dir, 'PyQt5', 'Qt', 'qml')

added_files = [
    (os.path.join(qml_dir, 'QtQuick'), '_qml/QtQuick'),
    (os.path.join(qml_dir, 'QtQuick.2'), '_qml/QtQuick.2'),
]

bin_files = []
for lib in [ 'libQt5Quick', 'libQt5Sql' ]:
        for found in glob.glob(site_packages_dir+'/PyQt5/Qt/lib/'+lib+'.*'):
                bin_files.append((found,'.'))
plugin_dest = 'qt5_plugins'
if os.name=='nt':
	plugin_dest = 'PyQt5/Qt/plugins'
for plugin in [ 'sqldrivers', 'egldeviceintegrations', 'xcbglintegrations' ]:
	if os.path.exists(site_packages_dir+'/PyQt5/Qt/plugins/'+plugin):
		bin_files.append((site_packages_dir+'/PyQt5/Qt/plugins/'+plugin,plugin_dest+'/'+plugin))

for dll in glob.glob(site_packages_dir+'/PyQt5/Qt/bin/*.dll'):
	bin_files.append((dll,'.'))
#for dll in [ 'libeay32.dll', 'qt5quick.dll', 'qt5sql.dll' ]:
#	if os.path.exists(site_packages_dir+'/PyQt5/Qt/bin/'+dll):
#		bin_files.append((site_packages_dir+'/PyQt5/Qt/bin/'+dll,'.'))


a = Analysis(['ui.py'],
             pathex=[os.getcwd()],
             binaries=bin_files,
             datas=added_files,
             hiddenimports=["queue"],
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
          exclude_binaries=True,
          name='cpmqdir',
          debug=False,
          strip=False,
          upx=True,
          console=True, icon='ui/icon.ico' )
coll = COLLECT(exe,
               a.binaries,
               Tree('ui',prefix='ui/'),
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='cpmqdir')

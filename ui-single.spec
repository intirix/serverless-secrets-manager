# -*- mode: python -*-

block_cipher = None

import os, site
from distutils.sysconfig import get_python_lib
import glob

qt5folder = "Qt5"

possible_site_packages_dir = [get_python_lib()] + site.getsitepackages()
possible_site_packages_dir = list(
    filter(
        lambda x: os.path.exists(os.path.join(x, "PyQt5", qt5folder, "qml")),
        possible_site_packages_dir,
    )
)

site_packages_dir = possible_site_packages_dir[0]
qml_dir = os.path.join(site_packages_dir, "PyQt5", qt5folder, "qml")
print("qml_dir=" + qml_dir)

added_files = [
    (os.path.join(qml_dir, "QtQuick"), "_qml/QtQuick"),
    (os.path.join(qml_dir, "QtQuick.2"), "_qml/QtQuick.2"),
]

bin_files = []
for lib in ["libQt5Quick", "libQt5Sql"]:
    for found in glob.glob(f"{site_packages_dir}/PyQt5/{qt5folder}/lib/" + lib + ".*"):
        bin_files.append((found, "."))
plugin_dest = "qt5_plugins"
if os.name == "nt":
    plugin_dest = f"PyQt5/{qt5folder}/plugins"
for plugin in ["egldeviceintegrations", "xcbglintegrations", "sqldrivers"]:
    if os.path.exists(f"{site_packages_dir}/PyQt5/{qt5folder}/plugins/" + plugin):
        bin_files.append(
            (
                f"{site_packages_dir}/PyQt5/{qt5folder}/plugins/" + plugin,
                plugin_dest + "/" + plugin,
            )
        )
        if os.name != "nt":
            bin_files.append(
                (
                    f"{site_packages_dir}/PyQt5/{qt5folder}/plugins/" + plugin,
                    f"PyQt5/{qt5folder}/plugins/" + plugin,
                )
            )
for plugin in ["sqldrivers"]:
        bin_files.append(
            (
                f"{site_packages_dir}/PyQt5/{qt5folder}/plugins/" + plugin,
                plugin,
            )
        )


bin_files.append(
    (glob.glob(site_packages_dir + "/scrypt.libs/libcrypto-*")[0], ".")
)
#bin_files.append(
#    (glob.glob(site_packages_dir + "/scrypt.libs/libz-*")[0], ".")
#)

a = Analysis(
    ["ui.py"],
    pathex=[os.getcwd()],
    binaries=bin_files,
    datas=added_files,
    hiddenimports=["queue"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

a.binaries.append(
    ("_scrypt", glob.glob(site_packages_dir + "/_scrypt*")[0], "EXTENSION")
)
print("site_packages=" + site_packages_dir)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    Tree("ui", prefix="ui/"),
    a.zipfiles,
    a.datas,
    name="cpmq",
    debug=False,
    strip=False,
    upx=True,
    console=True,
)

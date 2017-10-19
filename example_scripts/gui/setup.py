#setup.py
from cx_Freeze import setup, Executable
setup(
    name = "shp2d_2_3d_gui",
    version = "1.0.0",
    options = {"build_exe": {
        'packages': ["os","pyliburo","shapefile","gdal", "numpy"],
        'include_msvcr': True,
    }},
    executables = [Executable("shp2d_2_3d_gui.py",base="Win32GUI")]
    )
import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["tkinter", "pyaudio"], "include_files": ["ShowFiles/", "tcl86t.dll", "tk86t.dll", "favicon.ico"]}
os.environ['TCL_LIBRARY'] = r'C:\Users\Key Cohen Office\AppData\Local\Programs\Python\Python35\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\Key Cohen Office\AppData\Local\Programs\Python\Python35\tcl\tk8.6'
# Note that these paths are wrong :)

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Mr. Fair's Special Timer",
    version="1.1",
    description="Yovel made this, not you.",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon='favicon.ico')])

import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["tkinter", "pyaudio"],
                     "include_files": ["ShowFiles/", "tcl86t.dll", "tk86t.dll", "bin/", "README.txt"]}
os.environ['TCL_LIBRARY'] = r'C:\Users\Key Cohen Office\AppData\Local\Programs\Python\Python35\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\Key Cohen Office\AppData\Local\Programs\Python\Python35\tcl\tk8.6'

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Mr. Fair's Special Timer",
    version="1.3",
    description="Mr. Fairs stage crew timer. Made by Yovel Key-Cohen '21.",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon='bin/favicon.ico')])

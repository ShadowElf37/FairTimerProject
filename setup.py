import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["tkinter", "pyaudio"], "include_files": ["tcl86t.dll", "tk86t.dll", "default_config.cfg", "default_log.log"]}#, "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Mr. Fair's Special Timer",
        version = "1.0",
        description = "Yovel made this, not you.",
        options = {"build_exe": build_exe_options},
        executables = [Executable("main.py", base=base)])
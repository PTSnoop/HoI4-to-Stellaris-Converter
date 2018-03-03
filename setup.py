#!/usr/bin/python3

import sys
from cx_Freeze import setup, Executable

setup(name="HoI4 to Stellaris Converter",
      version="0.1",
      executables=[Executable("Converter.py")])

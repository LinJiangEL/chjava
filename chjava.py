#  Copyright (c) 2025. L.J.Afres, All rights reserved.

import os
import re
import sys
import winreg
import platform
from pathlib import Path

__version__ = "3.4.0"
chjava_help = """
    Command: chjava [-hv] [version]
    
      -h, --help        print this help message and exit
      -v, --version     print version and exit
      version           specify java version needed.
"""


def set_env_variable(name, value):
    """设置系统环境变量。"""
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
    winreg.CloseKey(key)
    os.system(f"set {name}={value}")

def get_windows_java_paths():
    paths = set()

    # 检查注册表
    reg_paths = [
        r"SOFTWARE\JavaSoft\Java Development Kit",
        r"SOFTWARE\JavaSoft\Java Runtime Environment",
        r"SOFTWARE\Wow6432Node\JavaSoft\Java Development Kit",
        r"SOFTWARE\Wow6432Node\JavaSoft\Java Runtime Environment"
    ]

    for reg_path in reg_paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    java_home, _ = winreg.QueryValueEx(subkey, "JavaHome")
                    exe_path = os.path.join(java_home, 'bin', 'java.exe')
                    if os.path.isfile(exe_path):
                        paths.add(exe_path)
                    i += 1
                except OSError:
                    break
        except FileNotFoundError:
            continue

    # 检查PATH环境变量
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    for path_dir in path_dirs:
        exe_path = os.path.join(path_dir, 'java.exe')
        if os.path.isfile(exe_path):
            paths.add(os.path.realpath(exe_path))

    # 检查常见安装目录
    prog_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
    java_dir = os.path.join(prog_files, 'Java')
    if os.path.isdir(java_dir):
        for entry in os.listdir(java_dir):
            exe_path = os.path.join(java_dir, entry, 'bin', 'java.exe')
            if os.path.isfile(exe_path):
                paths.add(os.path.realpath(exe_path))

    return list(paths)


def get_java_paths():
    system = platform.system()
    if system == 'Windows':
        javalist = get_windows_java_paths()
        return {int(re.findall(r'(?:jdk-|1\.)(\d+)', p)[0]): p for p in javalist}
    else:
        raise OSError("it only supported on Windows.")


JAVA_HOME = os.getenv('JAVA_HOME')
if os.getenv("PATH").lower().count("java") > 1:
    raise OSError("the environ PATH can not set any java path, instead of JAVA_HOME.")


def setjava(version):
    javas = get_java_paths()
    new_java = javas.get(int(version))
    if new_java is None:
        print(f"ValueError:cannot find java {version} in your computer, please put them in the directory C:\\Program Files\\Java.")
        return None
    else:
        new_java = str(Path(new_java).parent)
    if JAVA_HOME == new_java:
        print("OSError:a same JAVA_HOME already set.\n")
    else:
        set_env_variable("JAVA_HOME", new_java)
        print(f"Successfully change java version to {version}.\n")


try:
    version = sys.argv[1 if 1 < len(sys.argv) <= 2 else 0] if 1 < len(sys.argv) <= 2 else None
except IndexError:
    version = None
if version is None or version == "-h" or version == "--help":
    print(chjava_help)
elif version == "-v" or version == "--version":
    print(__version__)
else:
    if version.isdigit():
        setjava(version)
    else:
        pring("Fatal: [Error 2] invaild java version.\n")

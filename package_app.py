#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# 定义常量
APP_NAME = "医学影像体积计算"
MAIN_SCRIPT = "main.py"
OUTPUT_DIR = "dist"
ICON_PATH = "icon.png"

# 检查系统类型
def get_system_type():
    return platform.system()

# 检查是否安装了PyInstaller
def check_pyinstaller():
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

# 安装PyInstaller
def install_pyinstaller():
    print("正在安装PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("PyInstaller安装成功！")
    except subprocess.SubprocessError as e:
        print(f"安装PyInstaller失败: {e}")
        sys.exit(1)

# 清理旧的构建文件
def clean_old_builds():
    for dir_name in ["build", "dist", "__pycache__"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除旧的{dir_name}目录")

# 为不同平台生成PyInstaller命令
def generate_pyinstaller_command():
    system = get_system_type()
    cmd = [sys.executable, "-m", "PyInstaller"]
    
    # 通用选项
    cmd.extend([
        "--name", APP_NAME,
        "--onefile",  # 生成单个可执行文件
        "--windowed",  # 无控制台窗口
        "--distpath", OUTPUT_DIR,
    ])
    
    # 图标设置
    if os.path.exists(ICON_PATH):
        if system == "Windows":
            cmd.extend(["--icon", ICON_PATH])
        elif system == "Darwin":  # macOS
            cmd.extend(["--icon", ICON_PATH])
        else:  # Linux
            # Linux不支持直接使用PNG作为图标，需要转换为ico或使用其他格式
            pass
    else:
        print(f"警告: 未找到图标文件 {ICON_PATH}")
    
    # 平台特定选项
    if system == "Darwin":  # macOS
        # 确保Tkinter正常工作
        # 获取当前Python解释器路径
        python_path = sys.executable
        # 构建tkinter路径
        tkinter_path = os.path.join(os.path.dirname(os.path.dirname(python_path)), "lib", os.path.basename(sys.version.split()[0]), "tkinter")
        # 构建turtle路径
        turtle_path = os.path.join(os.path.dirname(os.path.dirname(python_path)), "lib", os.path.basename(sys.version.split()[0]), "turtle")
        
        # 检查路径是否存在
        if os.path.exists(tkinter_path):
            cmd.extend(["--add-data", f"{tkinter_path}:tkinter"])
        else:
            print(f"警告: 未找到tkinter库路径: {tkinter_path}")
            print("请确保已安装Python的Tk支持: brew install python-tk")
            sys.exit(1)
        
        if os.path.exists(turtle_path):
            cmd.extend(["--add-data", f"{turtle_path}:turtle"])
        else:
            print(f"警告: 未找到turtle库路径: {turtle_path}")
            print("请确保已安装Python的Tk支持: brew install python-tk")
            sys.exit(1)
    elif system == "Windows":
        # Windows下的额外选项
        pass
    else:  # Linux
        # Linux下的额外选项
        cmd.extend(["--add-data", "/usr/lib/python*/tkinter:tkinter"])
    
    # 添加主脚本
    cmd.append(MAIN_SCRIPT)
    
    return cmd

# 执行打包命令
def run_pyinstaller(cmd):
    print(f"正在执行打包命令: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"打包成功！可执行文件位于 {OUTPUT_DIR} 目录下")
    except subprocess.SubprocessError as e:
        print(f"打包失败: {e}")
        sys.exit(1)

# 主函数
def main():
    print(f"开始打包 {APP_NAME}...")
    print(f"当前系统: {get_system_type()}")
    
    # 检查并安装PyInstaller
    if not check_pyinstaller():
        install_pyinstaller()
    
    # 清理旧的构建文件
    clean_old_builds()
    
    # 生成并执行PyInstaller命令
    cmd = generate_pyinstaller_command()
    run_pyinstaller(cmd)
    
    print("打包完成！")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
py2exe 打包脚本 for Windows平台
使用方法:
1. 安装py2exe: pip install py2exe
2. 运行脚本: python setup_py2exe.py py2exe
"""

from distutils.core import setup
import py2exe
import sys
import os
from glob import glob

# 确保脚本以Windows GUI模式运行，而不是控制台模式
if len(sys.argv) == 1:
    sys.argv.append('py2exe')

# 获取项目根目录
project_dir = os.path.dirname(os.path.abspath(__file__))

# 定义额外需要包含的文件
additional_files = [
    (os.path.join(project_dir, 'icon.png'), 'icon.png'),
    (os.path.join(project_dir, 'requirements.txt'), 'requirements.txt'),
]

# 添加httpserver目录下的所有文件
httpserver_dir = os.path.join(project_dir, 'httpserver')
for root, dirs, files in os.walk(httpserver_dir):
    for file in files:
        file_path = os.path.join(root, file)
        dest_path = os.path.relpath(file_path, project_dir)
        additional_files.append((file_path, dest_path))

# 添加utils目录下的所有文件
utils_dir = os.path.join(project_dir, 'utils')
for root, dirs, files in os.walk(utils_dir):
    for file in files:
        file_path = os.path.join(root, file)
        dest_path = os.path.relpath(file_path, project_dir)
        additional_files.append((file_path, dest_path))

# 设置py2exe配置
setup(
    name='医学影像体积计算应用',
    version='1.0',
    description='医学影像体积计算工具，提供GUI界面和Web服务',
    author='',
    author_email='',
    windows=[{
        'script': 'main.py',
        'icon_resources': [(1, 'icon.png')],
        'dest_base': 'volumer',
    }],
    console=[{
        'script': 'start_server.py',
        'dest_base': 'start_server'
    }],
    options={
        'py2exe': {
            'bundle_files': 3,  # 不打包Python解释器
            'compressed': True,  # 压缩字节码
            'optimize': 2,  # 优化级别
            'includes': ['tkinter', 'fastapi', 'uvicorn', 'multipart'],
            'excludes': ['numpy', 'matplotlib'],  # 排除不需要的大型库
            'dll_excludes': ['MSVCP90.dll'],  # 排除系统已有的DLL
            'dist_dir': 'dist_windows',  # 输出目录
        }
    },
    data_files=additional_files,
    zipfile='lib/library.zip'
)

print('打包完成! 可执行文件位于 dist_windows 目录下')
# 医学影像体积计算应用

## 项目简介
这是一个用于医学影像体积计算的应用程序，提供了GUI界面和Web服务功能。

## 环境要求
- Python 3.8+ 
- 依赖包：fastapi, uvicorn, python-multipart
- Tkinter (通常是Python标准库的一部分)

## 安装依赖
在项目根目录下运行：
```bash
pip install -r requirements.txt
```

## 运行应用
### 直接运行
```bash
python main.py
```

### 使用Web服务
```bash
python start_server.py
```

## 打包应用
本项目提供了一个跨平台的打包脚本，可以将应用打包为单个可执行文件。

### 使用方法
1. 在项目根目录下运行打包脚本：
   ```bash
   python package_app.py
   ```

2. 打包完成后，可执行文件将位于`dist`目录下。

### 跨平台注意事项
#### Windows
- 确保已安装Python并添加到系统PATH
- 可能需要安装Microsoft Visual C++ Redistributable

#### macOS
- 如果遇到Tkinter相关错误，请确保已安装Python的Tk支持：
  ```bash
  brew install python-tk
  ```
- 打包后的应用可能需要签名才能正常运行

#### Linux
- 确保已安装tkinter：
  ```bash
  sudo apt-get install python3-tk  # Ubuntu/Debian
  sudo yum install python3-tkinter  # CentOS/RHEL
  ```
- 可能需要安装额外的依赖库

## 功能特点
1. GUI界面，操作简单直观
2. Web服务，支持批量处理
3. 实时状态显示
4. 结果自动计算和展示
5. 支持数据导出

## 目录结构
```
volumer/
├── main.py              # 主程序入口
├── start_server.py      # Web服务启动脚本
├── requirements.txt     # 依赖包列表
├── package_app.py       # 打包脚本
├── icon.png             # 应用图标
├── httpserver/          # Web服务相关代码
│   ├── api/             # API路由
│   └── static/          # 静态文件
├── utils/               # 工具类
└── log/                 # 日志文件
```
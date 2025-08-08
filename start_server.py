import os
import threading
import webbrowser
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from httpserver.api.routes import router as api_router

# 配置日志
log_dir = 'log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'server.log')

# 创建TimedRotatingFileHandler，按天轮转
handler = TimedRotatingFileHandler(
    log_file,
    when='midnight',
    interval=1,
    backupCount=30,
    encoding='utf-8'
)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# 获取uvicorn的logger
logger = logging.getLogger('uvicorn')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 创建 FastAPI 应用
app = FastAPI()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="httpserver/static"), name="static")

# 包含API路由
app.include_router(api_router)

# 启动服务器的函数
def start_server():
    try:
        print("正在启动服务器...")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", log_config=None)
    except Exception as e:
        print(f"服务器启动失败: {str(e)}")

# 启动应用
if __name__ == "__main__":
    print("医学影像体积计算服务器")
    print("1. 启动服务器并打开浏览器")
    print("2. 仅启动服务器")
    choice = input("请选择操作 (1/2): ")

    # 启动服务器线程
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    if choice == "1":
        # 延迟打开浏览器，确保服务器已启动
        time.sleep(2)
        webbrowser.open("http://localhost:8000")

    print("服务器已启动。按Ctrl+C停止。")
    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("正在停止服务器...")
        os._exit(0)
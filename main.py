#coding: utf8
import tkinter as tk
import os
import threading
import webbrowser
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from httpserver.api.routes import router as api_router

# 全局变量用于跟踪服务器状态
server_thread = None
server_running = False

# 创建 FastAPI 应用
app = FastAPI()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="httpserver/static"), name="static")

# 包含API路由
app.include_router(api_router)

# 启动服务器的函数
def start_server():
    global server_running
    server_running = True
    try:
        print("正在启动服务器...")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"服务器启动失败: {str(e)}")
        server_running = False

# 停止服务器的函数
def stop_server():
    global server_running
    server_running = False
    print("正在停止服务器...")
    if 'server_thread' in globals() and server_thread.is_alive():
        os._exit(0)  # 仅在开发环境中使用

# 创建 Tkinter 界面
def create_gui():
    global server_thread
    root = tk.Tk()
    # 设置窗口保持在最前台
    root.attributes('-topmost', True)
    # 设置窗口图标
    try:
        icon = tk.PhotoImage(file="icon.png")
        root.iconphoto(True, icon)
    except Exception as e:
        print(f"设置图标失败: {str(e)}")
    root.title("医学影像体积计算")
    root.geometry("300x160")
    # 设置窗口不可调整大小
    root.resizable(False, False)
    
    # 创建启动/停止服务器的按钮
    def toggle_server():
        global server_thread, server_running
        if not server_running:
            # 启动服务器
            try:
                server_thread = threading.Thread(target=start_server)
                server_thread.daemon = True  # 设置为守护线程，主程序结束时自动终止
                server_thread.start()
                # 更新按钮文本
                start_button.config(text="关闭Web服务器")
                # 添加状态标签
                status_label.config(text="服务器启动中...")
                # 延迟打开浏览器，确保服务器已启动
                root.after(2000, lambda: webbrowser.open("http://localhost:8000"))
                # 检查服务器状态
                root.after(3000, check_server_status)
            except Exception as e:
                print(f"启动服务器线程失败: {str(e)}")
                status_label.config(text="服务器启动失败")
        else:
            # 停止服务器
            stop_server()
            # 更新按钮文本
            start_button.config(text="启动Web服务器")
            status_label.config(text="服务器已停止")
    
    # 检查服务器状态
    def check_server_status():
        if server_running:
            status_label.config(text="服务器运行中...", fg="green")
        else:
            status_label.config(text="服务器启动失败", fg="red")
    
    start_button = tk.Button(root, text="启动Web服务器", command=toggle_server)
    start_button.pack(pady=30)
    
    # 添加说明标签
    label = tk.Label(root, text="点击按钮启动/关闭Web服务器，也可手动访问：\nhttp://localhost:8000/static/html/index.html")
    label.pack()
    
    # 添加状态标签
    global status_label
    status_label = tk.Label(root, text="服务器未启动", fg="red")
    status_label.pack(pady=10)
    
    root.mainloop()

# 启动应用
if __name__ == "__main__":
    create_gui()
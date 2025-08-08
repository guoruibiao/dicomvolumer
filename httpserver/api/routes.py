import os
from utils.filehelper import get_secondary_folders
from utils.volumer import get_volumer
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse


# 创建API路由器
router = APIRouter()

# 存储选择的文件夹路径和内容
selected_folder = None
folder_contents = []

dicom_directories = []  # 存储DICOM目录数据

@router.get("/")
def read_root():
    # 重定向到静态HTML文件
    return RedirectResponse(url="/static/html/index.html")

@router.post("/traverse_folder")
async def traverse_folder(request: Request):
    global dicom_directories
    
    # 获取请求数据
    data = await request.json()
    folder_path = data.get("folder_path")
    roi_file = data.get("roi_file")
    
    if not folder_path or not os.path.isdir(folder_path):
        return JSONResponse(content={"status": "error", "message": "无效的文件夹路径"})
    
    if not roi_file:
        return JSONResponse(content={"status": "error", "message": "ROI文件名不能为空"})
    
    # 遍历文件夹查找DICOM目录
    dicom_directories = []
    try:
        # 简单实现：假设所有子文件夹都是DICOM目录
        folders, msg, succ = get_secondary_folders(folder_path)
        if not succ:
            return JSONResponse(content={"status": "error", "message": msg})
        for dir_path in folders:
            dicom_directories.append({
                    "folder_path": dir_path,
                    "roi_file": roi_file,
                    "volume_result": None
                })
        # 简单实现：假设所有子文件夹都是DICOM目录
        # for root, dirs, files in os.walk(folder_path):
        #     for dir_name in dirs:
        #         dir_path = os.path.join(root, dir_name)
        #         dicom_directories.append({
        #             "folder_path": dir_path,
        #             "roi_file": roi_file,
        #             "volume_result": None
        #         })
        
        return JSONResponse(content={
            "status": "success",
            "message": f"成功遍历文件夹 '{folder_path}'",
            "dicom_directories": dicom_directories
        })
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"遍历文件夹失败: {str(e)}"})

@router.post("/calculate_volume")
async def calculate_volume(request: Request):
    # 获取请求数据
    data = await request.json()
    folder_path = data.get("folder_path")
    roi_file = data.get("roi_file")
    
    if not folder_path or not os.path.isdir(folder_path):
        return JSONResponse(content={"status": "error", "message": "无效的文件夹路径"})
    
    if not roi_file:
        return JSONResponse(content={"status": "error", "message": "ROI文件名不能为空"})

    # 修正roi_file相较于folder_path的路径
    parent_dir = os.path.dirname(folder_path)
    roi_file = os.path.join(parent_dir, roi_file)
    
    try:
        # 调用医学影像处理库来计算体积
        volumer = get_volumer(file_type='dicom')
        data_dict = volumer.get_volume(dicom_dir=folder_path, roi=roi_file)
        if not data_dict or len(data_dict) == 0:
            volume_result = "未计算出体积信息"
        else:
            volume_result = ""
            if len(data_dict) == 1:
                volume_result = f"{data_dict[list(data_dict.keys())[0]]['volume_mm3']:.3f}"
            else:
                for label, bucket in data_dict.items():
                    volume_result += f"label: {label}, bucket: {bucket['volume_mm3']:.3f}mm³\n"
        
        return JSONResponse(content={
            "status": "success",
            "message": "体积计算成功",
            "volume_result": volume_result,
        })
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"体积计算失败: {str(e)}"})

# 保留旧的端点以兼容可能的遗留代码
@router.post("/select_folder")
async def select_folder(request: Request):
    global selected_folder, folder_contents
    
    # 获取请求数据
    data = await request.json()
    selected_folder = data.get("folder_path")
    folder_contents = data.get("folder_contents", [])
    
    if selected_folder:
        return JSONResponse(content={"status": "success", "message": f"文件夹 '{selected_folder}' 选择成功", "folder_path": selected_folder})
    else:
        return JSONResponse(content={"status": "error", "message": "未选择文件夹"})

@router.get("/folder_contents")
def get_folder_contents():
    global folder_contents
    global folder_contents
    return {"files": folder_contents}
# coding: utf8
import os
import shutil


# 指定第几级目录下的全路径列表
def get_folders_by_level(root, level=-1):
    """
    获取指定层级的文件夹列表
    :param root:
    :param level:
    :return:
    """
    def _recursive(root, step=0, path=[]):
        nonlocal level
        if not os.path.exists(root):
            return
        if step == level:
            path.append(root)
            return
        ls = os.listdir(root)
        for item in ls:
            new_root = "{}{}{}".format(root, os.sep, item)
            if os.path.isfile(new_root):
                continue
            _recursive(new_root, step+1, path)

    paths = []
    if not os.path.exists(root):
        return paths, "root={} not exists".format(root), False

    _recursive(root, 0, paths)
    return paths, "success", True


# 获取末级目录的全路径
def get_secondary_folders(root):
    """
    获取最后一级的文件夹路径地址
    :param root:
    :return:
    """
    # check the root path exists or not
    if not os.path.exists(root):
        return [], "root={} not exists".format(root), False

    # TODO maybe there should have a white list

    folders = []
    for full_path, dir_name, filenames in os.walk(root):
        # print("full_path={}, dir_name={}, filenames={}".format(full_path, dir_name, filenames))
        if dir_name:
            continue
        if full_path in folders:
            continue
        folders.append(full_path)

    # return the target folders within `root`
    return folders, "success", True


# 删除以 prefix 为开头的文件
def remove_file_startswith(folder, prefix):
    if not os.path.exists(folder):
        return
    files = os.listdir(folder)
    for filename in files:
        if filename.startswith(prefix):
            fullpath = "{}{}{}".format(folder, os.sep, filename)
            print("removed: ", fullpath)
            # TODO real remove action


def date2int(datestr):
    length = len(datestr)
    if length == 6:
        return int(datestr[:2]) * 10 ** 4 + int(datestr[2:4]) * 10 ** 2 + int(datestr[4:])
    elif length == 8:
        return int(datestr[:4])*10**4 + int(datestr[4:6])*10**2 + int(datestr[6:])
    # 非预期格式不支持转换
    raise Exception("unsupported date format")


# 查找日期更老的子文件夹
def find_old_folder(folder):
    """
    查找日期更老的子文件夹
    :param folder:
    :return:
    """
    if not os.path.exists(folder):
        return "", "folder={} not exists".format(folder)
    ls = os.listdir(folder)
    ans, old = "", float('inf')
    for name in ls:
        new_folder = "{}{}{}".format(folder, os.sep, name)
        if not os.path.isdir(new_folder):
            continue
        intdate = date2int(name)
        if old < intdate:
            ans, old = new_folder, intdate
    return ans


def copy_file_or_folder(source, root, destination):
    # 如果目标文件夹路径不存在，创建路径
    source_is_folder = os.path.isdir(source)
    if source_is_folder:
        relative_path = source[len(root):]
        destination = "{}{}{}".format(destination, os.sep, relative_path)
        print("relative={}, dest={}".format(relative_path, destination))
        if os.path.exists(destination):
            shutil.rmtree(destination)
        os.makedirs(destination)
    else:
        if not os.path.exists(destination):
            os.makedirs(destination)

    # 判断输入的是文件还是文件夹
    if os.path.isfile(source):
        # 如果是文件，直接复制
        shutil.copy2(source, destination)
    elif os.path.isdir(source):
        # 如果是文件夹，复制整个文件夹
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        print("Error: The input path is not a file or folder.")
        return
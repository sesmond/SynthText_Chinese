#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Title   : 文件操作工具类
@File    :   file_utils.py    
@Author  : vincent
@Time    : 2020/6/3 9:40 上午
@Version : 1.0 
'''
import os
import glob


def escape_str(f_name):
    """
    转义字符能够执行
    :param f_name:
    :return:
    """
    f_name = f_name.replace(" ", "\ ")
    f_name = f_name.replace("(", "\(")
    f_name = f_name.replace(")", "\)")
    return f_name


def get_new_name(f_name):
    f_name = f_name.replace(" ", "")
    f_name = f_name.replace("(", "_")
    f_name = f_name.replace(")", "")
    return f_name


def copy_sub_file_to(parent_dir, dest_dir, exts):
    """
    移动文件夹下所有子目录的文件到目标文件夹
    :param parent_dir:
    :param dest_dir:
    :param exts:
    :return:
    """

    files = []
    # exts = ['jpg', 'png', 'jpeg', 'JPG']
    for parent, dirnames, filenames in os.walk(parent_dir):
        for filename in filenames:
            for ext in exts:
                if filename.lower().endswith(ext.lower()):
                    escape_name = escape_str(filename)
                    new_name = get_new_name(filename)
                    file_path = os.path.join(parent, escape_name)
                    last_dir = parent.split("/")[-1]
                    new_file_name = last_dir + "_" + new_name
                    new_path = os.path.join(dest_dir, new_file_name)
                    command = r"cp " + file_path + " " + new_path
                    print(command)
                    os.system(command)
                    break
    return files


def get_files(data_path, exts=['jpg', 'png', 'jpeg', 'JPG']):
    '''
    find image files in test data path
    :return: list of files found
    '''
    files = []
    for parent, dirnames, filenames in os.walk(data_path):
        for filename in filenames:
            for ext in exts:
                if filename.endswith(ext):
                    files.append(os.path.join(parent, filename))
                    break
    return files


def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))


def check_path(path):
    if not os.path.exists(path):
        print("路径不存在并创建：", path)
        os.makedirs(path)


def cmd_mv(from_f, to_f):
    cmd_mv_str = "mv " + from_f + " " + to_f
    os.system(cmd_mv_str)


def split():
    path = "images"
    files = get_files(path)
    check_path("validate.images")
    check_path("validate.labels")
    import random
    validate_files = random.sample(files, 50)
    for fp in validate_files:
        base_name = os.path.basename(fp)
        cmd_mv(fp, "validate.images/")
        label_name = os.path.splitext(base_name)[0] + ".txt"
        l1 = os.path.join("labels", label_name)
        cmd_mv(l1, "validate.labels")


if __name__ == '__main__':
    split()

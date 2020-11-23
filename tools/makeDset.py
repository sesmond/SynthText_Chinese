# -*- coding: UTF-8 -*-
import numpy as np
import h5py
import os, sys, traceback
import os.path as osp
import matplotlib.image as mpimg
"""
下载完的8000张背景 生成dset.h5文件
"""


ImageListDir = 'data/imagesName.txt'
ImagesDir = 'data/bg_img/'
seg_db = h5py.File('data/seg.h5', 'r')
depth_db = h5py.File('data/depth.h5', 'r')

# 生成的文件名
db = h5py.File('data/dset.h5', 'w')

input = open(ImageListDir, 'r')  # 将图片、seg文件、depth文件写入.h5w文件
imagesName = input.readlines()

image = db.create_group("image")
depth = db.create_group("depth")
seg = db.create_group("seg")
num = 0
for name in seg_db['mask']:
    name = name.rstrip("\n")
    try:
        img = mpimg.imread(ImagesDir + name)
        d = depth_db[name][:]
        s = seg_db['mask'][name][:]
    except:
        continue
    image[name] = img
    s_max = np.amax(s)
    label = range(1, s_max + 1)
    area = range(1, s_max + 1)
    for i in label:
        area[i - 1] = int(np.sum(s == i))
    depth[name] = d
    seg[name] = s
    seg[name].attrs['area'] = area
    seg[name].attrs['label'] = label

    num = num + 1
    print( num)
    print(name + 'is ok!\n')

db.close()
seg_db.close()
depth_db.close()
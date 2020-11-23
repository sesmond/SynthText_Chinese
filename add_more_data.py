import numpy as np
import h5py
import os, sys, traceback
import os.path as osp
import wget, tarfile
import cv2
from PIL.Image import Image

"""
往数据集里添加数据
"""


def get_data(data_path):
    """
    Download the image,depth and segmentation data:
    Returns, the h5 database.
    """
    return h5py.File(data_path, 'r')


def add_more_data_into_dset(db_fname, more_img_file_path, more_depth_path, more_seg_path):
    db = h5py.File(db_fname, 'wb+')
    # TODO depth 和 seg是干什么的？
    depth_db = get_data(more_depth_path)
    seg_db = get_data(more_seg_path)
    db.create_group('image')
    db.create_group('depth')
    db.create_group('seg')
    for imname in os.listdir(more_img_file_path):
        if imname.endswith('.jpg'):
            full_path = more_img_file_path + imname
            print(full_path, imname)

            j = Image.open(full_path)
            imgSize = j.size
            rawData = j.tostring()
            img = Image.fromstring('RGB', imgSize, rawData)
            # img = img.astype('uint16')
            db['image'].create_dataset(imname, data=img)
            #  TODO
            db['depth'].create_dataset(imname, data=depth_db[imname])
            db['seg'].create_dataset(imname, data=seg_db['mask'][imname])
            db['seg'][imname].attrs['area'] = seg_db['mask'][imname].attrs['area']
            db['seg'][imname].attrs['label'] = seg_db['mask'][imname].attrs['label']
    db.close()
    depth_db.close()
    seg_db.close()


if __name__ == '__main__':
    # path to the data-file, containing image, depth and segmentation:
    db_fname = 'data/dset_test.h5'

    # add more data into the dset
    more_depth_path = "data/depth.h5"
    more_seg_path = '/seg.h5'
    # 新增的背景图片
    more_img_file_path = 'bg_img/'

    add_more_data_into_dset(db_fname, more_img_file_path, more_depth_path, more_seg_path)

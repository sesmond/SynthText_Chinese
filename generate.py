# -*- coding: utf-8 -*-

import csv
import numpy as np
import h5py
import os, sys, traceback
from multiprocessing import Process, Pool

import os.path as osp
from synthgen import *
from common import *
import wget, tarfile
import cv2 as cv
import time
import logging
import pickle as cp
from utils import json_utils, file_utils

logger = logging.getLogger(__name__)

# 一张图片生成几张样本
INSTANCE_PER_IMAGE = 1  # no. of times to use the same image
# TODO!!!!
# 生成一张样本的超时时间
# SECS_PER_IMG = 50  # max time per image in seconds
SECS_PER_IMG = None
# path to the data-file, containing image, depth and segmentation:
# 相关配置文件路径
DATA_PATH = 'data'

depth_db = None
seg_db = None


def save_result_json(output_path, imgname, res):
    """
        把生成的坐标和图片保存
    """
    img_op = os.path.join(output_path, "images")
    file_utils.check_path(img_op)
    msg_op = os.path.join(output_path, "message")
    file_utils.check_path(msg_op)
    txt_op = os.path.join(output_path, "labels")
    file_utils.check_path(txt_op)

    ninstance = len(res)
    for i in range(ninstance):
        print(colorize(Color.GREEN, 'added into the db %s ' % res[i]['txt']))
        temp = res[i]
        img = temp['img']
        word_bb = temp['wordBB']
        char_bb = temp['charBB']
        txt = temp['txt']
        # TODO 有换行符的是两个box
        new_text = []
        for line in txt:
            arr = line.split("\n")
            new_text.extend(arr)
        # (n,4,2) 把顺序调整为正常
        word_boxes = np.transpose(word_bb).astype('uint8')
        #
        dname = "%s_%d" % (imgname, i) + ".jpg"
        print(dname, new_text)
        img_file = os.path.join(img_op, dname)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(img_file, img)
        result_json = {
            'text': new_text,
            'word_pos': word_bb.tolist(),
            'char_pos': char_bb.tolist()
        }
        json_utils.write_json(msg_op, dname, result_json)
        # TODO 统一格式
        # 写 labels 四点坐标+ 文本，逗号隔开
        txt_name = os.path.splitext(dname)[0] + ".txt"
        f2 = open(os.path.join(txt_op, txt_name), 'w', encoding='utf-8')
        writer = csv.writer(f2)
        for j in range(len(txt)):
            box = word_boxes[j]
            word = new_text[j]
            line = np.append(box.reshape(-1), word)
            writer.writerow(line)
        f2.close()


def rgb2hsv(image):
    return image.convert('HSV')


def rgb2gray(image):
    rgb = np.array(image)

    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]

    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


def main(viz=False, worker=5):
    logger.info("开始处理,viz:%r,%r", viz, worker)

    # TODO 进程数
    im_dir = 'data/8000/bg_img'
    output_path = "data/8000/output/"

    global depth_db, seg_db
    depth_db = h5py.File('data/8000/depth.h5', 'r')
    seg_db = h5py.File('data/8000/seg.h5', 'r')

    imnames = sorted(depth_db.keys())
    img_cnt = len(imnames)

    with open('data/8000/imnames.cp', 'rb') as f:
        filtered_imnames = set(cp.load(f))

    # 分批多线程处理
    file_list_arr = np.array_split(imnames, worker)
    logger.info("线程数：%r,总文件数：%r", worker, len(imnames))
    p_no = 0
    pool = Pool(processes=worker)

    for file_list in file_list_arr:
        time.sleep(2)
        pool.apply_async(generate_batch, args=(p_no, im_dir, file_list, output_path, viz))
        p_no += 1
    pool.close()
    pool.join()
    logger.info("程序处理结束，全部生成完毕！")


def generate_batch(p_no, im_dir, im_list, output_path, viz=False):
    """
    批量生成样本
    """
    global depth_db, seg_db
    img_cnt = len(im_list)
    logger.info("进程：%r,处理文件数：", p_no, img_cnt)
    # 初始化渲染器？
    rv3 = RendererV3(DATA_PATH, max_time=SECS_PER_IMG)
    for i, im_name in enumerate(im_list):
        img_p = osp.join(im_dir, im_name)
        logger.info("进程：%r,总第[%r-%r]开始，%r", p_no, img_cnt, i, img_p)
        if not os.path.exists(img_p):
            logger.warning("文件：%r不存在，跳过", img_p)
            continue
        #
        dname = "%s_%d" % (im_name, 0) + ".jpg"
        check_path = os.path.join(output_path, "images", dname)
        if os.path.exists(check_path):
            logger.info("已经生成过了不再执行：%r", check_path)
            continue

        t1 = time.time()
        try:
            # get the colour image:
            img = Image.open(img_p).convert('RGB')

            # get depth:
            depth = depth_db[im_name][:].T
            depth = depth[:, :, 0]

            # get segmentation info:
            seg = seg_db['mask'][im_name][:].astype('float32')
            area = seg_db['mask'][im_name].attrs['area']
            label = seg_db['mask'][im_name].attrs['label']

            # re-size uniformly:
            sz = depth.shape[:2][::-1]
            img = np.array(img.resize(sz, Image.ANTIALIAS))
            seg = np.array(Image.fromarray(seg).resize(sz, Image.NEAREST))

            print(colorize(Color.RED, '%d of %d' % (i, img_cnt - 1), bold=True))
            # 往空隙里贴文字
            # depth(w,h): 里面每个像素的深度值
            # seg(w,h): 里面每个像素的区分后的值1，2，3这样把图片分块了
            # area 对应里面每个分块的面积？
            # label 对应每个分块的标号，1，2，3
            res = rv3.render_text(img, depth, seg, area, label,
                                  ninstance=INSTANCE_PER_IMAGE, viz=viz)
            t2 = time.time()
            # print 'time consume in each pic',t2-t1

            for ct in range(5):
                print("len res:", len(res))
                if len(res) > 0:
                    # non-empty : successful in placing text:
                    save_result_json(output_path, im_name, res)
                    break
                else:
                    res = rv3.render_text(img, depth, seg, area, label,
                                          ninstance=INSTANCE_PER_IMAGE, viz=viz)
            # visualize the output:
            print('time consume in each pic', t2 - t1)
            logger.info("进程：%r,总第[%r-%r]结束，%r", p_no, img_cnt, i, img_p)
            if viz:
                # TODO
                # continue
                if 'q' in input(colorize(Color.RED, 'continue? (enter to continue, q to exit): ', True)):
                    break
        except:
            traceback.print_exc()
            print(colorize(Color.GREEN, '>>>> CONTINUING....', bold=True))
            continue

    logger.info("进程：%r 处理结束。", p_no)


def init_log():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[:%(lineno)d] - %(levelname)s : %(message)s')


if __name__ == '__main__':
    init_log()
    import argparse

    parser = argparse.ArgumentParser(description='Genereate Synthetic Scene-Text Images')
    parser.add_argument('-v', '--viz', default=False, help='flag for turning on visualizations')
    parser.add_argument('-w', '--worker', type=int, default=5, help='num of workers')

    args = parser.parse_args()
    main(args.viz, args.worker)

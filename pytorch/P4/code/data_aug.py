"""
此代码实现了将数据集左右翻转并合并生成新的数据集

待改进：
 * 文件夹的判空操作，本代码在处理数据之前，应该先将文件夹创建好，架构如下
    |-data
        |-ori_data
        |-res_data
    |-new_data

 * 此代码只能实现图片左右翻转，如需实现上下反转以及其他的数据增强操作，需重写 imgaug() 函数下的 seq 部分(建议查看函数源码)(line48)
"""

import imgaug.augmenters as iaa
import os
from PIL import Image
import numpy as np
import re
import shutil
import glob


def data_aug(input_path, output_path,  new_data_path):
    """主函数，用于调用其他函数"""

    if not os.path.exists(input_path):
        os.mkdir(input_path)
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    if not os.path.exists(new_data_path):
        os.mkdir(new_data_path)

    imgaug(input_path, output_path)
    rename_img(output_path)
    merge_files(new_data_path, input_path, output_path)


def imgaug(input_path, output_path):
    """获取原图片文件路径和翻转后生成图片路径"""

    input_dirs = [d for d in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, d))]
    output_dirs = [d for d in os.listdir(output_path) if os.path.isdir(os.path.join(output_path, d))]

    for i in range(len(input_dirs)):
        input_dirs[i] = input_path + "/" + input_dirs[i]

    for i in range(len(output_dirs)):
        output_dirs[i] = output_path + "/" + output_dirs[i]

    seq = iaa.Sequential([
        iaa.Flipud(1.0),  # 按垂直轴随机翻转50%的图片
    ])

    len_class = len(input_dirs)  # 获取文件夹中子目录长度

    for i in range(len_class):
        for file_name in os.listdir(input_dirs[i]):
            if file_name.endswith('.jpg') or file_name.endswith('.jpeg') or file_name.endswith('.png'):
                file_path = os.path.join(input_dirs[i], file_name)
                img = Image.open(file_path)

                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                img_arr = np.array(img)
                img_aug = seq(images=img_arr)
                img_aug = Image.fromarray(img_aug)

                if img_aug.mode == 'RGBA':
                    img_aug = img_aug.convert('RGB')

                output_file_path = os.path.join(output_dirs[i], file_name)
                img_aug.save(output_file_path)

def rename_img(folder_path):
    """将生成的新文件夹中图片按照顺序重命名"""

    counters = {}  # 定义一个空字典

    for folder_name in os.listdir(folder_path):
        folder = os.path.join(folder_path, folder_name)
        if os.path.isdir(folder):
            file_types = ['*.jpg', '*.jpeg', '*.png']  # 文件类型可以根据实际情况修改
            total_files = 0
            for file_type in file_types:
                total_files += len(glob.glob(os.path.join(folder, file_type)))
            counters[folder_name] = total_files  # 将文件夹名和图片数量添加到字典中
    # 使用字典推导式将字典中的每个键值加1
    counters = {key: value + 1 for key, value in counters.items()}

    # 遍历每个子文件夹
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)

        # 如果是文件夹，则遍历文件夹中所有文件
        if os.path.isdir(subfolder_path):

            # 获取当前子文件夹的起始计数器
            counter = counters[subfolder]

            for name in os.listdir(subfolder_path):
                # 如果是图片文件，则解析文件名并重命名文件
                if name.endswith('.jpg') or name.endswith('.jpeg') or name.endswith('.png'):
                    # 解析文件名中的关键信息
                    pattern = r'(\w+)_(\d+)/.(jpg|jpeg|png)'
                    match = re.match(pattern, name)
                    if match:
                        keyword, number, extension = match.groups()
                    else:
                        keyword = subfolder
                        number = counter
                        extension = os.path.splitext(name)[1][1:]

                    # 构造新的文件名
                    new_name = keyword + str(number) + '.' + extension
                    # 使用os.rename函数重命名文件
                    os.rename(os.path.join(subfolder_path, name), os.path.join(subfolder_path, new_name))
                    # 更新计数器变量
                    counter += 1


def merge_files(new_data_path, input_path, output_path):
    """合并原数据集和新数据集"""

    new_data_dirs = [d for d in os.listdir(new_data_path) if os.path.isdir(os.path.join(new_data_path, d))]

    for i in range(len(new_data_dirs)):
        new_data_dirs[i] = new_data_path + "/" + new_data_dirs[i]

    len_class = len(new_data_dirs)
    input_dirs = [d for d in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, d))]
    output_dirs = [d for d in os.listdir(output_path) if os.path.isdir(os.path.join(output_path, d))]

    for i in range(len(input_dirs)):
        input_dirs[i] = input_path + "/" + input_dirs[i]

    for i in range(len(output_dirs)):
        output_dirs[i] = output_path + "/" + output_dirs[i]



    for i in range(len_class):
        # 如果合并文件夹不存在，创建一个新的文件夹

        if not os.path.exists(new_data_dirs[i]):
            os.mkdir(new_data_dirs[i])

        # 遍历文件夹1中的所有文件，并复制到合并文件夹中
        for filename in os.listdir(input_dirs[i]):
            if filename.endswith(".jpg"):  # 只复制图片文件
                src_path = os.path.join(input_dirs[i], filename)
                dst_path = os.path.join(new_data_dirs[i], filename)
                shutil.copyfile(src_path, dst_path)

        # 遍历文件夹2中的所有文件，并复制到合并文件夹中
        for filename in os.listdir(output_dirs[i]):
            if filename.endswith(".jpg"):  # 只复制图片文件
                src_path = os.path.join(output_dirs[i], filename)
                dst_path = os.path.join(new_data_dirs[i], filename)
                shutil.copyfile(src_path, dst_path)

        print("图片已成功合并到新文件夹！")

if __name__ == "__main__":

    input_path = r"/Users/montylee/NJUPT/Learn/Github/deeplearning/pytorch/P4/datasets/ori_data" # 原数据集路径
    output_path = r"/Users/montylee/NJUPT/Learn/Github/deeplearning/pytorch/P4/datasets/new_data" # 反转后存放数据集的路径
    new_data_path = r"/Users/montylee/NJUPT/Learn/Github/deeplearning/pytorch/P4/datasets/res_data" # 最终两个数据集合并后的路径

    data_aug(input_path, output_path,  new_data_path)


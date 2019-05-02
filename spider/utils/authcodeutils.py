#-*- coding: utf-8 -*-
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import pytesseract
import os
import time


# 获取指定目录下验证码文件列表
image_path = "C:\\Users\\PAN\\Desktop\\img"

def get_files(path):
    file_list = []
    files = os.listdir(path)
    for f in files:
        if(os.path.isfile(path + '\\' + f)):
            file_list.append(path + '\\' + f)
    return file_list

# 高斯滤波器
def guassian_blur(img, a, b):
    #（a,b）为高斯核的大小，0 为标准差, 一般情况a,b = 5
    blur = cv2.GaussianBlur(img,(a,b),0)
    # 阈值一定要设为 0！
    ret, th = otsu_s(blur)
    return ret, th

# 均值滤波器
def hamogeneous_blur(img):
    blur = cv2.blur(img,(5,5))
    ret, th = otsu_s(blur)
    return ret, th

# 中值滤波器
def median_blur(img):
    blur = cv2.medianBlur(img,5)
    ret, th = otsu_s(blur)
    return ret, th

#双边滤波器
def bilatrial_blur(img):
    blur = cv2.bilateralFilter(img,9,75,75)
    ret, th = otsu_s(blur)
    return ret, th

def otsu_s(img):
    ret, th = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return ret, th

def main():
    """
    测试模糊处理后otsu's二值化
    :return:
    """
    file_list = get_files(image_path)
    for filename in file_list:
        print(filename)
        img = cv2.imread(filename, 0)
        ret1, th1 = guassian_blur(img, 5, 5)
        ret2, th2 = bilatrial_blur(img)

        cv2.imwrite('temp1.png', th1)
        cv2.imwrite('temp2.png', th2)

        titles = ['original', 'guassian', 'bilatrial']
        images = [img, th1, th2]
        for i in range(3):
            plt.subplot(1,3,i+1),plt.imshow(images[i], 'gray')
            plt.title(titles[i])
            plt.xticks([]),plt.yticks([])
        plt.show()

        image1 = Image.open("temp1.png")
        image2 = Image.open("temp2.png")
        image3 = Image.open(filename)

        print(pytesseract.image_to_string(image1, lang='eng', config='--psm 6'))
        print(pytesseract.image_to_string(image2, lang='eng', config='--psm 6'))
        print(pytesseract.image_to_string(image3, lang='eng', config='--psm 6'))


if __name__ == '__main__':
    main()

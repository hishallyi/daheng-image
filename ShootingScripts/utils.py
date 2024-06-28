"""
@Author : Hishallyi
@Date   : 2024/6/27
@Code   : 工具函数
"""

import datetime

from PIL import Image, ImageTk


def print_promotion(message):
    """
    打印提示信息
    @param message: 提示信息
    @return: null
    """
    print("")
    print("-------------------------------------------------------------")
    if message is not None:
        print(message)
    print("-------------------------------------------------------------")
    print("")


def print_variable(var_name, var):
    """
    打印变量信息
    @param var_name: 变量名
    @param var: 变量值
    @return: null
    """
    print("********** %s: %s **********" % (var_name, var))


def images_acquisition(cam_object):
    while True:
        raw_image = cam_object.data_stream[0].get_image()  # 采集raw_image
        if raw_image is None:
            print_promotion("raw_image图像获取失败！")
            continue
        rgb_image = raw_image.convert("RGB")

        # TODO：实现图像增强
        # rgb_image.image_improvement(color_correction_param, contrast_lut, gamma_lut)

        numpy_image = rgb_image.get_numpy_array()  # 从RGB图像数据创建numpy数组
        return numpy_image


def save_img(cam):
    sn = cam.DeviceSerialNumber.get()
    cam.stream_on()
    # 采集图像并实时显示
    numpy_image = images_acquisition(cam)
    img = Image.fromarray(numpy_image, 'RGB')  # 展示获取的图像

    saved_path = "D:\FileDevelop\DevelopTools\Pycharm\DaHengImage\Galaxy\CaptureByScripts\\"  # 图像保存路径
    mtime = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')

    img.save(saved_path + mtime + str("-") + sn + ".jpg")  # 保存图片到本地
    cam.stream_off()

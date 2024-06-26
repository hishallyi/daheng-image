"""
@Author  ：Hishallyi
@Date    ：2024/6/26
@Code    : 拍摄流程
"""
import sys
import os
import time

import gxipy as gx
from PIL import Image
import datetime

# 指定Python解释器路径
work_path = os.path.abspath('')
project_path = os.path.dirname(work_path)
sys.path.append(project_path)


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


def save_images(final_img, i, saved_path):
    """
    保存图像
    @param final_img: Image库从Array转换的图像
    @param i: 图像编号
    @param saved_path: 图像保存路径
    @return: null
    """
    mtime = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    final_img.save(
        saved_path + mtime + str("-") + str(
            i) + ".jpg")  # 保存图片到本地


def camera_params_setting(cam):
    """
    设置相机参数
    @param cam: 相机对象
    @return: null
    """
    # 设置相机参数
    cam.Width.set(2448)
    cam.Height.set(2048)

    # 拍摄参数变量
    framerate_set = 20  # 帧率
    balance_ratio_set = 0.5  # 白平衡
    exposure_time_set = 1000000  # 曝光时间

    cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.ON)  # 打开帧率设置模式
    cam.AcquisitionFrameRate.set(framerate_set)  # 设置帧率

    # cam.BalanceRatio.set(balance_ratio_set)  # 设置白平衡
    cam.BalanceWhiteAuto.set(gx.GxSwitchEntry.ON)  # 设置自动白平衡

    cam.ExposureTime.set(exposure_time_set)  # 设置曝光时间
    # cam.BalanceWhiteAuto.set(gx.GxSwitchEntry.ON)  # 设置自动曝光

    # 设置相机增益


def acquisition_setting(cam, saved_path):
    """
    相机采集过程设置
    @param cam: 相机对象
    @return: 保存采集图像
    """
    # 拍摄图像
    cam.stream_on()

    # 打印相机采集流信息
    print_variable("相机采集流信息 cam.data_stream", cam.data_stream)
    print_variable("相机采集信息流 cam.data_stream 的数量", len(cam.data_stream))

    # 采集3张图像
    for i in range(3):
        raw_image = cam.data_stream[0].get_image()

        frame_get = cam.CurrentAcquisitionFrameRate.get()

        if raw_image is None:
            print_promotion("raw_image图像获取失败！")
            continue
        rgb_image = raw_image.convert("RGB")
        # rgb_image.image_improvement(color_correction_param, contrast_lut, gamma_lut)  # 实现图像增强

        numpy_image = rgb_image.get_numpy_array()  # 从RGB图像数据创建numpy数组
        img = Image.fromarray(numpy_image, 'RGB')  # 展示获取的图像

        save_images(img, i, saved_path)
        print_promotion("第 %s 张图像保存成功！当前采集帧率为 %s " % (i + 1, frame_get))


if __name__ == "__main__":
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list()
    if dev_num == 0:
        print_promotion("Number of enumerated devices is 0")
    else:
        print_promotion("创建设备成功，设备数量为:%d" % dev_num)

    # 打开一个相机进行拍摄
    cam = device_manager.open_device_by_index(1)
    print_promotion("相机已经打开！，SN号为：%s" % dev_info_list[0].get("sn"))

    camera_params_setting(cam)  # 设置相机参数

    print_promotion("相机参数设置完成！等待5秒后开始采集图像！")
    time.sleep(10)  # 参数设置完成之后需要等待5秒

    saved_path = "D:\FileDevelop\DevelopTools\Pycharm\DaHengImage\Galaxy\CaptureByScripts\\"  # 图像保存路径
    acquisition_setting(cam, saved_path)  # 采集过程设置

    # 设备配置信息
    remote_device_feature = cam.get_remote_device_feature_control()
    print_variable("remote_device_feature", remote_device_feature)
    # 本地配置信息
    local_device_feature = cam.get_local_device_feature_control()
    print_variable("local_device_feature", local_device_feature)
    # 流配置信息
    stream_feature = cam.get_stream(1).get_featrue_control()  # 大恒把函数名字写错了！！！是feature，不是feature
    print_variable("stream_feature", stream_feature)

    # 导入导出相机配置参数
    # remote_device_feature.feature_load("camera_config_file.txt")
    # remote_device_feature.feature_save("camera_config_file.txt")

    # 关闭相机
    cam.close_device()
    print_promotion("摄像机已经关闭！")

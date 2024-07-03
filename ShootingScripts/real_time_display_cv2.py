"""
@Author : Hishallyi
@Date   : 2024/6/27
@Code   : 连接单个相机，仅使用cv2+滑动条来实时显示图像
"""

import sys
import os
import time
import cv2
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


def save_images(final_img, saved_path):
    """
    保存图像
    @param final_img: Image库从Array转换的图像
    @param i: 图像编号
    @param saved_path: 图像保存路径
    @return: null
    """
    mtime = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    # final_img.save(saved_path + mtime + str("-") + str(i) + ".jpg")  # 保存图片到本地
    final_img.save(saved_path + mtime + str("-") + ".jpg")  # 保存图片到本地


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
    gain_set = 4.0  # 增益
    black_level_set = 0  # 黑电平

    # 帧采集率
    cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.ON)  # 打开帧率设置模式
    cam.AcquisitionFrameRate.set(framerate_set)  # 设置帧率

    # 白平衡
    # cam.BalanceRatio.set(balance_ratio_set)  # 设置白平衡系数  TODO：gxipy.Exception.InvalidAccess: BalanceRatio.set: is not writeable
    cam.BalanceWhiteAuto.set(gx.GxAutoEntry.ONCE)  # 设置自动白平衡

    # 曝光
    cam.ExposureTime.set(exposure_time_set)  # 设置曝光时间
    # cam.ExposureAuto.set(gx.GxAutoEntry.ONCE)  # 设置自动曝光

    # 相机增益
    cam.Gain.set(gain_set)  # 设置增益
    # cam.GainAuto.set(gx.GxAutoEntry.ONCE)  # 设置自动增益

    # 黑电平
    cam.BlackLevel.set(black_level_set)  # 设置黑电平
    # cam.BlackLevelAuto.set(gx.GxAutoEntry.OFF)  # 设置自动黑电平

    # 坏点矫正
    # cam.DeadPixelCorrect.set(gx.GxSwitchEntry.ON)  # 打开坏点矫正  TODO：gxipy.Exception.InvalidAccess: DeadPixelCorrect.set: is not writeable

    # 设备配置信息
    remote_device_feature = cam.get_remote_device_feature_control()  # <gxipy.FeatureControl.FeatureControl object at 0x000001B9E6CB83D0>
    # 导出相机配置参数
    remote_device_feature.feature_save("camera_config_file.txt")


# 定义参数更新的回调函数
def update_exposure_time(val):
    cam.ExposureTime.set(val)


def update_gain(val):
    cam.Gain.set(val)


def acquisition_setting(cam, saved_path):
    """
    相机采集过程设置
    @param cam: 相机对象
    @return: 保存采集图像
    """
    # 设备配置信息
    remote_device_feature = cam.get_remote_device_feature_control()  # <gxipy.FeatureControl.FeatureControl object at 0x000001B9E6CB83D0>
    # 本地配置信息
    # local_device_feature = cam.get_local_device_feature_control()  # <gxipy.FeatureControl.FeatureControl object at 0x000001B9E6CB8340>
    # 流配置信息
    # stream_feature = cam.get_stream(1).get_featrue_control()  # <gxipy.FeatureControl.FeatureControl object at 0x000001B9E6CB8160> 大恒把函数名字写错了！！！是feature，不是feature

    # 导入相机配置参数
    remote_device_feature.feature_load("camera_config_file.txt")

    # 创建窗口和滑动条
    window_height = 816
    window_width = 683
    cv2.namedWindow('Live Image')
    cv2.resizeWindow('Live Image', window_height, window_width)  # 设置窗口大小
    cv2.moveWindow('Live Image', 100, 100)  # 设置窗口位置

    cv2.createTrackbar('Exposure Time', 'Live Image', 1000000, 1000000, update_exposure_time)
    cv2.createTrackbar('Gain', 'Live Image', 4, 10, update_gain)

    # 拍摄图像
    cam.stream_on()

    # 打印相机采集流信息
    # print_variable("相机采集流信息 cam.data_stream", cam.data_stream)  # [<gxipy.DataStream.DataStream object at 0x000001B9E6CABEB0>]
    # print_variable("相机采集信息流 cam.data_stream 的数量", len(cam.data_stream))  # 1

    global img

    while True:
        raw_image = cam.data_stream[0].get_image()

        frame_get = cam.CurrentAcquisitionFrameRate.get()

        if raw_image is None:
            print_promotion("raw_image图像获取失败！")
            continue
        rgb_image = raw_image.convert("RGB")

        # TODO：实现图像增强
        # rgb_image.image_improvement(color_correction_param, contrast_lut, gamma_lut)

        numpy_image = rgb_image.get_numpy_array()  # 从RGB图像数据创建numpy数组
        img = Image.fromarray(numpy_image, 'RGB')  # 展示获取的图像
        numpy_image_resized = cv2.resize(numpy_image, (window_height, window_width))  # 确保图像适合窗口大小
        numpy_image_rgb = cv2.cvtColor(numpy_image_resized, cv2.COLOR_BGR2RGB)

        cv2.imshow('Live Image', numpy_image_rgb)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # 按 'q' 键退出
            break

    save_images(img, saved_path)
    # print_promotion("第 %s 张图像保存成功！当前采集帧率为 %s " % (i + 1, frame_get))
    print_promotion("图像保存成功！当前采集帧率为 %s " % frame_get)

    cam.stream_off()


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

    # camera_params_setting(cam)  # 设置相机参数

    print_promotion("相机参数设置完成！等待5秒后开始采集图像！")
    time.sleep(5)  # 参数设置完成之后需要等待5秒

    saved_path = "D:\FileDevelop\DevelopTools\Pycharm\DaHengImage\Galaxy\CaptureByScripts\\"  # 图像保存路径
    acquisition_setting(cam, saved_path)  # 采集过程设置

    # 关闭相机
    cam.close_device()
    cv2.destroyAllWindows()
    print_promotion("摄像机已经关闭！")

    """
    如果报错：gxipy.Exception.InvalidAccess: DeviceManager.open_device_by_index:{-8}
    {Access denied:{-1005}{GenICam::Client::CGVCPCtrlPort::SetPrivilege:line[546]}{TLError:When write CCP register,the requested device is denied.}}
    表示相机打开没有关闭，需要关闭相机再用程序打开
    """

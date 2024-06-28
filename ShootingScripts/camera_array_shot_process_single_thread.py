"""
@Author : Hishallyi
@Date   : 2024/6/27
@Code   : 相机拍摄流程——单线程控制GUI(CamDisplayGUi)报错！！！
@problem: tkinter窗口控件点击之后，OpenCV窗口不显示
"""

import sys
import os
import threading
import time
import cv2
import gxipy as gx
import tkinter as tk
from tkinter import messagebox

from utils import *

# 指定Python解释器路径
work_path = os.path.abspath('')
project_path = os.path.dirname(work_path)
sys.path.append(project_path)

device_manager = gx.DeviceManager()
dev_num, dev_info_list = device_manager.update_device_list()
if dev_num == 0:
    print_promotion("Number of enumerated devices is 0")
else:
    print_promotion("创建设备成功，设备数量为:%d" % dev_num)

camera_sn_list = [dev_info.get("sn") for dev_info in dev_info_list]
cameras = []
cameras_dict = {}
# 通过设备序列号打开设备
for sn in camera_sn_list:
    try:
        cam = device_manager.open_device_by_sn(sn)
        cameras.append(cam)
        cameras_dict[sn] = cam
        print_promotion("打开设备 %s 成功！" % sn)
    except Exception as e:
        print_promotion("打开设备 %s 失败！！！打印错误信息:%s" % (sn, e))
        continue

# 统一载入相机配置文件
for cam in cameras:
    remote_device_feature = cam.get_remote_device_feature_control()
    remote_device_feature.feature_load("camera_config_file.txt")

print_promotion("载入相机配置文件成功！等待相机采集流程......")
time.sleep(5)

window_height = 816
window_width = 683


def real_time_display(camera_sn):
    """
    实时显示采集图像
    @return:
    """
    print(camera_sn)
    chosen_cam = cameras_dict[camera_sn]
    print(chosen_cam)
    chosen_cam.stream_on()
    while True:
        try:
            raw_image = chosen_cam.data_stream[0].get_image()
            if raw_image is None:
                continue
            rgb_image = raw_image.convert("RGB")
            numpy_image = rgb_image.get_numpy_array()  # 从RGB图像数据创建numpy数组
            numpy_image_resized = cv2.resize(numpy_image, (window_height, window_width))  # 确保图像适合窗口大小
            numpy_image_rgb = cv2.cvtColor(numpy_image_resized, cv2.COLOR_BGR2RGB)
            cv2.imshow('Live Image', numpy_image_rgb)
        except Exception as e:
            print_promotion("实时显示图像失败！打印错误信息:%s" % e)
            break
    # 保存该相机的配置参数
    # chosen_remote_device_feature = chosen_cam.get_remote_device_feature_control()
    # chosen_remote_device_feature.feature_save("camera_config_file.txt")
    chosen_cam.stream_off()


def cam_params_confirm(camera_sn, white_balance_ratio, exposure_time, gain, black_level):
    """
    确认相机参数并返回给
    @return:
    """

    if camera_sn == '请选择相机':
        messagebox.showinfo(title='提示', message='请先选择相机！')
    else:
        cam = cameras_dict[camera_sn]
        if white_balance_ratio and exposure_time and gain and black_level != '':
            try:
                # cam.WhiteBalanceRatio.set(float(white_balance_ratio))  # 会报错，先不设置
                cam.ExposureTime.set(int(exposure_time))
                cam.Gain.set(float(gain))
                cam.BlackLevel.set(int(black_level))

                messagebox.showinfo(title='提示', message='相机参数设置成功！')
            except Exception as e:
                print_promotion("相机参数设置失败！打印错误信息:%s" % e)
        else:
            messagebox.showinfo(title='提示', message='请填写完整相机参数！')


# GUI选择相机，实时查看采集图像，动态更新相机参数--------------------------------
class CamDisplayGUI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # 创建OpenCV窗口
        cv2.namedWindow('Live Image')
        cv2.resizeWindow('Live Image', 816, 683)  # 设置窗口大小
        cv2.moveWindow('Live Image', 100, 100)  # 设置窗口位置

        # cv2.createTrackbar('Exposure Time', 'Live Image', 1000000, 1000000, update_exposure_time)
        # cv2.createTrackbar('Gain', 'Live Image', 4, 10, update_gain)

        # 按字母q退出
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


opencv_thread = CamDisplayGUI()
opencv_thread.start()

# 创建Tkinter窗口
root = tk.Tk()
root.title("Camera Settings")

# 下拉框和标签
tk.Label(root, text="Camera List").grid(row=0, column=0)
camera_list = tk.StringVar(root)
camera_list.set("请选择相机")  # 设置默认选项
camera_option = tk.OptionMenu(root, camera_list, *camera_sn_list)
camera_option.grid(row=0, column=1)
camera_list.trace("w", lambda *args: real_time_display(camera_list.get()))

# 创建输入框和标签
tk.Label(root, text="White Balance Ratio").grid(row=1, column=0)
white_balance_entry = tk.Entry(root)
white_balance_entry.grid(row=1, column=1)

tk.Label(root, text="Exposure Time").grid(row=2, column=0)
exposure_time_entry = tk.Entry(root)
exposure_time_entry.grid(row=2, column=1)

tk.Label(root, text="Gain").grid(row=3, column=0)
gain_entry = tk.Entry(root)
gain_entry.grid(row=3, column=1)

tk.Label(root, text="Black Level").grid(row=4, column=0)
black_level_entry = tk.Entry(root)
black_level_entry.grid(row=4, column=1)

# 相机参数确定按钮
confirm_button = tk.Button(root, text="Confirm Params",
                           command=lambda: cam_params_confirm(camera_list.get(), white_balance_entry.get(),
                                                              exposure_time_entry.get(), gain_entry.get(),
                                                              black_level_entry.get()))
confirm_button.grid(row=5, column=1)

# 启动Tkinter主循环
root.mainloop()

# 保存图像----------------------------------------------------------------
print_promotion("开始相机采集流程......")
for cam in cameras:
    save_img(cam)

# 关闭相机
for cam in cameras:
    try:
        cam.close_device()
    except Exception as e:
        print_promotion("关闭设备 %s 失败！！！打印错误信息:%s" % (cam, e))
        continue
print_promotion("所有设备关闭成功！")

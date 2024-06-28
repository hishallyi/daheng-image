"""
@Author : Hishallyi
@Date   : 2024/6/27
@Code   : 相机拍摄流程——仅使用tkinter来显示图像
"""

import sys
import os
import threading
import time
import cv2
import gxipy as gx
import tkinter as tk
from tkinter import messagebox, ttk

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


def real_time_display(camera_sn):
    """
    实时显示采集图像
    @return:
    """
    if camera_sn == '':
        messagebox.showinfo(title='提示', message='请先选择相机！')
    else:
        chosen_cam = cameras_dict[camera_sn]
        chosen_cam.stream_on()
        # 循环来保证相机一直在采集
        while True:
            try:
                raw_image = chosen_cam.data_stream[0].get_image()
                if raw_image is None:
                    continue
                rgb_image = raw_image.convert("RGB")
                numpy_image = rgb_image.get_numpy_array()  # 从RGB图像数据创建numpy数组

                # Resize图像以适应显示区域
                image = Image.fromarray(numpy_image).resize((640, 480), Image.LANCZOS)
                image_tk = ImageTk.PhotoImage(image=image)
                image_label.config(image=image_tk)
                image_label.image = image_tk
                root.update_idletasks()
                if root.quit:
                    break
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

    if camera_sn == '':
        messagebox.showinfo(title='提示', message='请先选择相机！')
    else:
        cam = cameras_dict[camera_sn]
        if white_balance_ratio and exposure_time and gain and black_level != '':
            try:
                print_promotion(f"{white_balance_ratio}, {exposure_time}, {gain}, {black_level}")
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

# 创建Tkinter窗口
root = tk.Tk()
root.title("相机控制面板")

# 设置窗口大小和布局
root.geometry("800x600")
root.resizable(False, False)

# 下拉框和标签
serial_label = tk.Label(root, text="选择相机序列号:")
serial_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
serial_var = tk.StringVar()
serial_combobox = ttk.Combobox(root, textvariable=serial_var)
serial_combobox['values'] = camera_sn_list
serial_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")

# 输入框标签
param_labels = ["白平衡", "曝光时间", "增益", "黑电平"]
param_entries = []
for i, label in enumerate(param_labels):
    tk.Label(root, text=label).grid(row=i+1, column=0, padx=10, pady=5, sticky="w")
    entry = tk.Entry(root)
    entry.grid(row=i+1, column=1, padx=10, pady=5, sticky="w")
    param_entries.append(entry)

# 用于显示图像的Label
image_frame = tk.Frame(root, width=640, height=480)
image_frame.grid(row=0, column=2, rowspan=6, padx=10, pady=10)
image_frame.grid_propagate(False)  # 防止自动调整大小
image_label = tk.Label(image_frame)
image_label.pack()

# 开始采集按钮
start_button = tk.Button(root, text="开始采集", command=lambda: real_time_display(serial_var.get()))
start_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# 相机参数确定按钮
confirm_button = tk.Button(root, text="Confirm Params",
                           command=lambda: cam_params_confirm(serial_var.get(), param_entries[0].get(),
                                                              param_entries[1].get(), param_entries[2].get(),
                                                              param_entries[3].get()))
confirm_button.grid(row=6, column=1, columnspan=2, padx=10, pady=10)

# 启动Tkinter主循环
root.mainloop()

# 保存图像----------------------------------------------------------------
print_promotion("开始相机采集流程......")
# TODO：统一导入相机参数后再进行采集
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

"""
@Author : Hishallyi
@Date   : 2024/6/28
@Code   : ChatGPT写的阵列拍摄脚本2
"""

import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import gxipy as gx
import sys
import os

# 指定Python解释器路径
work_path = os.path.abspath('')
project_path = os.path.dirname(work_path)
sys.path.append(project_path)


# 初始化相机并获取所有相机序列号
def init_cameras():
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list()
    cameras = [device_manager.open_device_by_index(i + 1) for i in range(dev_num)]
    serial_numbers = []
    cameras_dict = {}
    for camera in cameras:
        sn = camera.DeviceSerialNumber.get()
        serial_numbers.append(sn)
        cameras_dict[sn] = camera
    return cameras, serial_numbers, cameras_dict


cameras, serial_numbers, cameras_dict = init_cameras()

# 创建Tkinter GUI
root = tk.Tk()
root.title("相机控制面板")

# 下拉框
serial_var = tk.StringVar()
serial_combobox = ttk.Combobox(root, textvariable=serial_var)
serial_combobox['values'] = serial_numbers
serial_combobox.grid(row=0, column=0, padx=10, pady=10)

# 输入框
param_entries = []
for i in range(4):
    entry = tk.Entry(root)
    entry.grid(row=i + 1, column=0, padx=10, pady=10)
    param_entries.append(entry)

# OpenCV窗口显示
cv2.namedWindow('Camera View')


# 选择相机并开始采集
def start_camera():
    selected_serial = serial_var.get()
    print(selected_serial)
    cam = cameras_dict[selected_serial]
    print(cam)
    cam.stream_on()
    while True:
        raw_image = cam.data_stream[0].get_image()
        if raw_image is None:
            continue
        rgb_image = raw_image.convert("RGB")
        numpy_image = rgb_image.get_numpy_array()
        cv2.imshow('Camera View', numpy_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.stream_off()


# 设置相机参数
def set_camera_params():
    selected_serial = serial_var.get()
    params = [entry.get() for entry in param_entries]
    cam = cameras_dict[selected_serial]
    cam.ExposureTime.set(float(params[0]))
    cam.Gain.set(float(params[1]))
    # cam.BalanceWhiteAuto.set(params[2])
    # cam.PixelFormat.set(params[3])


# 导出相机参数
def export_camera_params():
    selected_serial = serial_var.get()
    cam = cameras_dict[selected_serial]
    remote_device_feature = cam.get_remote_device_feature_control()
    remote_device_feature.feature_save("camera_config_file_test.txt")


# 按钮
start_button = tk.Button(root, text="开始采集", command=start_camera)
start_button.grid(row=5, column=0, padx=10, pady=10)

set_button = tk.Button(root, text="设置参数", command=set_camera_params)
set_button.grid(row=6, column=0, padx=10, pady=10)

export_button = tk.Button(root, text="导出参数", command=export_camera_params)
export_button.grid(row=7, column=0, padx=10, pady=10)

root.mainloop()
cv2.destroyAllWindows()

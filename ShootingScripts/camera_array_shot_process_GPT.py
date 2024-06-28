"""
@Author : Hishallyi
@Date   : 2024/6/28
@Code   : ChatGPT写的阵列拍摄脚本
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import json
import os


# 读取相机阵列，获得所有相机序列号列表
def get_camera_serials():
    # 假设这是获取相机序列号的函数
    return ["12345678", "23456789", "34567890"]


# 初始化相机并加载参数配置
def init_camera(serial):
    # 假设这是初始化相机的函数，并加载相机参数配置
    cap = cv2.VideoCapture(int(serial[-1]))  # 假设用序列号的最后一位作为摄像头ID
    if not cap.isOpened():
        raise ValueError(f"Camera with serial {serial} could not be opened.")
    return cap


# 更新相机参数
def update_camera_params(cap, params):
    # 假设这是设置相机参数的函数
    for param, value in params.items():
        cap.set(param, value)


# 导出相机参数配置
def export_camera_params(serial, params):
    with open(f"{serial}_params.json", "w") as f:
        json.dump(params, f, indent=4)


class CameraApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Camera Control")

        self.serials = get_camera_serials()
        self.current_camera = None
        self.current_serial = None
        self.params = {
            "brightness": 0,
            "contrast": 0,
            "saturation": 0,
            "gain": 0
        }

        # Tkinter GUI布局
        self.create_widgets()
        self.update_gui()

    def create_widgets(self):
        self.serial_label = tk.Label(self.master, text="Camera Serial")
        self.serial_label.grid(row=0, column=0)

        self.serial_combobox = ttk.Combobox(self.master, values=self.serials)
        self.serial_combobox.grid(row=0, column=1)
        self.serial_combobox.bind("<<ComboboxSelected>>", self.on_serial_selected)

        self.param_labels = {}
        self.param_entries = {}
        row = 1
        for param in self.params:
            label = tk.Label(self.master, text=param.capitalize())
            label.grid(row=row, column=0)
            self.param_labels[param] = label

            entry = tk.Entry(self.master)
            entry.grid(row=row, column=1)
            self.param_entries[param] = entry
            row += 1

        self.confirm_button = tk.Button(self.master, text="Confirm", command=self.confirm_params)
        self.confirm_button.grid(row=row, column=0, columnspan=2)

        self.export_button = tk.Button(self.master, text="Export Parameters", command=self.export_params)
        self.export_button.grid(row=row + 1, column=0, columnspan=2)

    def update_gui(self):
        for param, entry in self.param_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(self.params[param]))

    def on_serial_selected(self, event):
        serial = self.serial_combobox.get()
        if self.current_camera:
            self.current_camera.release()
        self.current_camera = init_camera(serial)
        self.current_serial = serial
        self.show_camera()

    def show_camera(self):
        if not self.current_camera:
            return
        while True:
            ret, frame = self.current_camera.read()
            if not ret:
                break
            cv2.imshow("Camera View", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    def confirm_params(self):
        try:
            params = {param: int(entry.get()) for param, entry in self.param_entries.items()}
            update_camera_params(self.current_camera, params)
            self.params.update(params)
            self.show_camera()
        except ValueError as e:
            messagebox.showerror("Parameter Error", f"Invalid parameter value: {e}")

    def export_params(self):
        if self.current_serial:
            export_camera_params(self.current_serial, self.params)
            messagebox.showinfo("Export Success", f"Parameters for camera {self.current_serial} exported successfully.")
        else:
            messagebox.showerror("Export Error", "No camera selected for exporting parameters.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()

"""
@Author  ：Hishallyi
@Date    ：2024/6/19
@Code    : 多相机控制界面
光圈调到最小
曝光时间：1000000 一百万 最大曝光时间，关闭自动曝光
增益：3.8dB
白平衡：设置为continue
采集帧率：每秒20帧
"""

import tkinter as tk
from tkinter import ttk
import gxipy as gx
import numpy as np
import cv2
from threading import Thread


class CameraControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Camera Control GUI")

        # Initialize camera parameters
        self.exposure_time_var = tk.DoubleVar(value=100000.0)
        self.white_balance_var = tk.StringVar(value='CONTINUOUS')

        # Initialize ui component
        self.create_widgets()

        self.device_manager = gx.DeviceManager()

        # Update device list
        self.update_device_list()

    def update_device_list(self):
        self.dev_num, self.dev_info_list = self.device_manager.update_device_list()
        if self.dev_num == 0:
            raise Exception("No device found")
        self.cameras = [self.device_manager.open_device_by_index(i + 1) for i in range(self.dev_num)]

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Exposure Time:").grid(row=0, column=0, sticky=tk.W)
        self.exposure_entry = ttk.Entry(frame, textvariable=self.exposure_time_var)
        self.exposure_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="White Balance:").grid(row=1, column=0, sticky=tk.W)
        self.white_balance_combobox = ttk.Combobox(frame, textvariable=self.white_balance_var)
        self.white_balance_combobox['values'] = ('OFF', 'ONCE', 'CONTINUOUS')
        self.white_balance_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E))

        self.start_button = ttk.Button(frame, text="Start", command=self.start_cameras)
        self.start_button.grid(row=2, column=0, sticky=tk.W)

        self.stop_button = ttk.Button(frame, text="Stop", command=self.stop_cameras)
        self.stop_button.grid(row=2, column=1, sticky=tk.W)

        self.quit_button = ttk.Button(frame, text="Quit", command=self.root.quit)
        self.quit_button.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        frame.columnconfigure(1, weight=1)

    def start_cameras(self):
        for cam in self.cameras:
            cam.ExposureAuto.set(gx.GxAutoEntry.OFF)  # Disable auto exposure
            cam.ExposureTime.set(self.exposure_time_var.get())
            cam.BalanceWhiteAuto.set(getattr(gx.GxAutoEntry, self.white_balance_var.get()))

            cam.stream_on()

        self.capture_thread = Thread(target=self.capture_images)
        self.capture_thread.start()

    def capture_images(self):
        while True:
            for cam in self.cameras:
                raw_image = cam.data_stream[0].get_image()
                if raw_image is None:
                    continue

                numpy_image = raw_image.get_numpy_array()
                if numpy_image is None:
                    continue

                # Display the image
                cv2.imshow(f'Camera {cam.DeviceSerialNumber.get()}', numpy_image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    def stop_cameras(self):
        for cam in self.cameras:
            cam.stream_off()
            cv2.destroyAllWindows()

        if hasattr(self, 'capture_thread') and self.capture_thread.is_alive():
            self.capture_thread.join()

    def quit(self):
        self.stop_cameras()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraControlApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import ttk
import gxipy as gx
import numpy as np
import cv2
from PIL import Image, ImageTk
from threading import Thread


class CameraControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Camera Control")
        self.root.geometry("800x600")  # 设置初始窗口大小

        self.device_manager = gx.DeviceManager()
        self.cameras = []
        self.selected_camera = None
        self.stop_event = False

        self.create_widgets()
        self.update_device_list()

    def update_device_list(self):
        try:
            self.dev_num, self.dev_info_list = self.device_manager.update_device_list()
            if self.dev_num == 0:
                raise Exception("No device found")
            # 确保释放之前的设备
            self.close_all_cameras()
            self.cameras = [self.device_manager.open_device_by_index(i + 1) for i in range(self.dev_num)]
            self.camera_combobox['values'] = [cam.DeviceID.get() for cam in self.cameras]
        except gx.WinError as e:
            print(f"Error updating device list: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def close_all_cameras(self):
        for cam in self.cameras:
            try:
                cam.close_device()
            except gx.GxError as e:
                print(f"Error closing camera: {e}")

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 相机选择下拉框
        ttk.Label(frame, text="Select Camera:").grid(row=0, column=0, sticky=tk.W)
        self.camera_var = tk.StringVar()
        self.camera_combobox = ttk.Combobox(frame, textvariable=self.camera_var, state="readonly")
        self.camera_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.camera_combobox.bind("<<ComboboxSelected>>", self.select_camera)

        # 实时显示区域
        self.display_label = ttk.Label(frame)
        self.display_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Quit button
        self.quit_button = ttk.Button(frame, text="Quit", command=self.quit)
        self.quit_button.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

    def select_camera(self, event):
        selected_device_id = self.camera_var.get()
        self.selected_camera = next(cam for cam in self.cameras if cam.DeviceID.get() == selected_device_id)

        # Start the thread to update the display
        self.stop_event = False
        self.display_thread = Thread(target=self.update_display)
        self.display_thread.start()

    def update_display(self):
        if self.selected_camera is None:
            return

        self.selected_camera.stream_on()

        while not self.stop_event:
            raw_image = self.selected_camera.data_stream[0].get_image()
            if raw_image is None:
                continue

            numpy_image = raw_image.get_numpy_array()
            if numpy_image is None:
                continue

            # 调整图像大小以适应标签组件
            image = Image.fromarray(numpy_image)
            image = image.resize((self.display_label.winfo_width(), self.display_label.winfo_height()), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image)
            self.display_label.configure(image=image)
            self.display_label.image = image

        self.selected_camera.stream_off()

    def quit(self):
        self.stop_event = True
        if hasattr(self, 'display_thread') and self.display_thread.is_alive():
            self.display_thread.join()

        self.close_all_cameras()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraControlApp(root)
    root.mainloop()

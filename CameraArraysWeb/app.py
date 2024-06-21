"""
@Author  ：Hishallyi
@Date    ：2024/6/20
@Code    :
"""

from flask import Flask, render_template, request, jsonify
from utils import *

import sys
import os
import gxipy as gx
from PIL import Image
import datetime
import time

# 指定Python解释器的搜索路径
notebook_path = os.path.abspath('')
project_root = os.path.dirname(notebook_path)
sys.path.append(project_root)

# 创建Flask应用
app = Flask(__name__)

cameras = []
camera_serials = []


def init_cameras():
    global cameras, camera_serials
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list()
    if dev_num == 0:
        raise Exception("No device found")
    else:
        print_promotion("创建设备成功，设备数量为:%d" % dev_num)

    for dev_info in dev_info_list:
        camera = device_manager.open_device_by_sn(dev_info.get("sn"))
        cameras.append(camera)
    camera_serials = [cam.DeviceSerialNumber.get() for cam in cameras]


# 初始化相机
init_cameras()


@app.route('/')
def index():
    try:
        return render_template('index.html', camera_serials=camera_serials)
    except Exception as e:
        return f"An error occurred: {e}", 500


@app.route('/set_parameters', methods=['POST'])
def set_parameters():
    exposure_time = float(request.form.get('exposure_time'))
    white_balance = request.form.get('white_balance')
    for cam in cameras:
        cam.ExposureTime.set(exposure_time)
        cam.BalanceWhiteAuto.set(gx.GxAutoEntry.CONTINUOUS if white_balance == 'CONTINUOUS' else gx.GxAutoEntry.OFF)
    return jsonify({'status': 'success', 'message': 'Parameters set successfully'})


@app.route('/capture_image/<serial>')
def capture_image(serial):
    cam = next(cam for cam in cameras if cam.get_device_info().get('sn') == serial)
    raw_image = cam.data_stream[0].get_image()
    rgb_image = raw_image.convert("RGB")
    numpy_image = rgb_image.get_numpy_array()

    # Save the image to a temporary file and send it back to the client
    import cv2
    cv2.imwrite(f'static/temp_{serial}.jpg', numpy_image)
    return jsonify({'image_url': f'/static/temp_{serial}.jpg'})


if __name__ == '__main__':
    app.run(debug=True)

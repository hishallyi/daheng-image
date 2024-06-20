"""
@Author  ：Hishallyi
@Date    ：2024/6/20
@Code    :
"""

from flask import Flask, render_template, request, jsonify
import gxipy as gx

app = Flask(__name__)

# Initialize the device manager and open all cameras
device_manager = gx.DeviceManager()
dev_num, dev_info_list = device_manager.update_device_list()
cameras = [device_manager.open_device_by_index(i + 1) for i in range(dev_num)]


# Function to set camera parameters
def set_camera_parameters(exposure_time, white_balance):
    for cam in cameras:
        cam.ExposureTime.set(exposure_time)
        cam.BalanceWhiteAuto.set(gx.GxSwitchEntry.CONTINUOUS if white_balance == 'CONTINUOUS' else gx.GxSwitchEntry.OFF)


@app.route('/')
def index():
    camera_serials = [cam.get_device_info().get('sn') for cam in cameras]
    return render_template('index.html', camera_serials=camera_serials)


@app.route('/set_parameters', methods=['POST'])
def set_parameters():
    exposure_time = float(request.form.get('exposure_time'))
    white_balance = request.form.get('white_balance')
    set_camera_parameters(exposure_time, white_balance)
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

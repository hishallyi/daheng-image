"""
@Author  ：Hishallyi
@Date    ：2024/6/12
@Code    : 相机拍摄脚本demo1
"""
import gxipy as gx
from PIL import Image
import datetime


def print_promotion(message):
    print("")
    print("**********************************************************")
    if message is not None:
        print(message)


def set_shooting_params(cam, framerate_set):
    width_set = 2448  # 设置分辨率宽
    height_set = 2048  # 设置分辨率高

    # 设置宽和高
    cam.Width.set(width_set)
    cam.Height.set(height_set)

    # 设置连续采集
    # cam.TriggerMode.set(gx.GxSwitchEntry.OFF) # 设置触发模式
    cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.ON)

    # 设置帧率
    cam.AcquisitionFrameRate.set(framerate_set)
    print_promotion("用户设置的帧率为:%d fps" % framerate_set)
    framerate_get = cam.CurrentAcquisitionFrameRate.get()  # 获取当前采集的帧率
    print("当前采集的帧率为:%d fps" % framerate_get)

    return framerate_get


def main():
    framerate_set = 20  # 设置帧率
    num = 10  # 采集帧率次数（为调试用，可把后边的图像采集设置成while循环，进行无限制循环采集）

    # 1. 创建设备管理对象
    device_manager = gx.DeviceManager()

    # 2. 枚举设备
    dev_num, dev_info_list = device_manager.update_device_list()
    if dev_num == 0:
        print("Number of enumerated devices is 0")
        return
    else:
        print_promotion("创建设备成功，设备号为:%d" % dev_num)

    # 3. 通过设备序列号打开设备
    cam = device_manager.open_device_by_sn(dev_info_list[0].get("sn"))
    # 如果是黑白相机，则不支持
    if cam.PixelColorFilter.is_implemented() is False:  # is_implemented判断枚举型属性参数是否已实现
        print("该示例不支持黑白相机.")
        cam.close_device()
        return
    else:
        print_promotion("打开彩色摄像机成功，SN号为：%s" % dev_info_list[0].get("sn"))

    # 4. 设置属性参数
    framerate_get = set_shooting_params(cam, framerate_set)

    # 5. 开始数据采集
    print_promotion("开始数据采集......")
    print("")
    cam.stream_on()

    # 采集图像
    for i in range(num):
        raw_image = cam.data_stream[0].get_image()  # 打开第0通道数据流
        if raw_image is None:
            print("获取彩色原始图像失败.")
            continue
        rgb_image = raw_image.convert("RGB")  # 从彩色原始图像获取RGB图像
        if rgb_image is None:
            continue
        # rgb_image.image_improvement(color_correction_param, contrast_lut, gamma_lut)  # 实现图像增强
        numpy_image = rgb_image.get_numpy_array()  # 从RGB图像数据创建numpy数组
        if numpy_image is None:
            continue
        img = Image.fromarray(numpy_image, 'RGB')  # 展示获取的图像
        # img.show()
        mtime = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        img.save(r"D:\FileDevelop\DevelopTools\Pycharm\DaHengImage\Galaxy\CaptureByScripts\\" + mtime + str("-") + str(
            i) + ".jpg")  # 保存图片到本地
        print("Frame ID: %d   Height: %d   Width: %d   framerate_set:%dfps   framerate_get:%dfps"
              % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width(), framerate_set,
                 framerate_get))  # 打印采集的图像的高度、宽度、帧ID、用户设置的帧率、当前采集到的帧率

    # 6. 停止采集，关闭设备
    cam.stream_off()
    cam.close_device()
    print_promotion("摄像机已经停止采集，设备已经关闭！")


if __name__ == "__main__":
    main()

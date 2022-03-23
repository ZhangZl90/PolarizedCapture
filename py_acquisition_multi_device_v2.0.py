# @Author:ZhangZl
# @Date:30/11/2021

import datetime
import os
import threading
import time

import cv2
import numpy as np
from arena_api.system import system

isQuit = False
left_images = []
right_images = []


def create_devices_with_tries():
    tries = 0
    tries_max = 6
    sleep_time_secs = 10
    while tries < tries_max:  # Wait for device for 60 seconds
        devices = system.create_device()
        if not devices:
            print(
                f'Try {tries + 1} of {tries_max}: waiting for {sleep_time_secs} '
                f'secs for a device to be connected!')
            for sec_count in range(sleep_time_secs):
                time.sleep(1)
                print(f'{sec_count + 1} seconds passed ',
                      '.' * sec_count, end='\r')
            tries += 1
        else:
            print(f'Created {len(devices)} device(s)')
            return devices
    else:
        raise Exception(f'No device found! Please connect a device and run '
                        f'the example again.')


def configure_some_nodes(device):
    tl_stream_nodemap = device.tl_stream_nodemap
    # Enable stream auto negotiate packet size
    tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True
    # Enable stream packet resend
    tl_stream_nodemap['StreamPacketResendEnable'].value = True
    # make sure the device sends images continuously

    nodemap = device.nodemap
    nodemap['AcquisitionMode'].value = 'Continuous'
    # white balance
    nodemap['BalanceWhiteEnable'].value = True
    nodemap['BalanceWhiteAuto'].value = 'Continuous'
    # ExposureAuto
    nodemap['ExposureAuto'].value = 'Continuous'
    # Gain
    nodemap['GainAuto'].value = 'Off'
    # nodemap['Gain'].value = nodemap['Gain'].max

    # automate the calculation of max FPS whenever the device settings change
    nodemap['AcquisitionFrameRateEnable'].value = True
    # set FPS node to max FPS which was set to be automatically calculated
    # base on current device settings
    nodemap['AcquisitionFrameRate'].value = nodemap['AcquisitionFrameRate'].max
    # max FPS according to the current settings
    nodemap['DeviceStreamChannelPacketSize'].value = nodemap['DeviceStreamChannelPacketSize'].max

    # Set features before streaming.-------------------------------------------
    nodes = device.nodemap.get_node(['Width', 'Height', 'PixelFormat'])
    # Set width and height to their max values
    nodes['Width'].value = nodes['Width'].max
    nodes['Height'].value = nodes['Height'].max
    nodes['PixelFormat'].value = "PolarizedAngles_0d_45d_90d_135d_BayerRG8"
    safe_print(f'Node Configure finished successfully!')


def get_RGB8_image(buffer_array):
    image_d0 = cv2.cvtColor(buffer_array[:, :, 0], cv2.COLOR_BayerRG2RGB)
    image_d45 = cv2.cvtColor(buffer_array[:, :, 1], cv2.COLOR_BayerRG2RGB)
    image_d90 = cv2.cvtColor(buffer_array[:, :, 2], cv2.COLOR_BayerRG2RGB)
    image_d135 = cv2.cvtColor(buffer_array[:, :, 3], cv2.COLOR_BayerRG2RGB)

    return [image_d0, image_d45, image_d90, image_d135]


def get_cat_image(image_list):
    image_d0 = image_list[0]
    # cv2.putText(image_d0, "degree 0", (10, 45), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1.5, thickness=2, color=(0, 0, 255))
    image_d45 = image_list[1]
    # cv2.putText(image_d45, "degree 45", (10, 45), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1.5, thickness=2, color=(0, 0, 255))
    image_d90 = image_list[2]
    # cv2.putText(image_d90, "degree 90", (10, 45), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1.5, thickness=2, color=(0, 0, 255))
    image_d135 = image_list[3]
    # cv2.putText(image_d135, "degree 135", (10, 45), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1.5, thickness=2, color=(0, 0, 255))
    img1 = np.concatenate((image_d0, image_d45), axis=1)
    img2 = np.concatenate((image_d90, image_d135), axis=1)
    image_cat = np.concatenate((img1, img2), axis=0)

    return image_cat


def save_images(image_lists, save_dir):
    now = datetime.datetime.now()
    now_string = str(now)
    left_save_dir = f'''{save_dir[0]}/{now.year}-{now.month}-{now.day}'''
    if not os.path.exists(left_save_dir):
        os.makedirs(left_save_dir)
    right_save_dir = f'''{save_dir[1]}/{now.year}-{now.month}-{now.day}'''
    if not os.path.exists(right_save_dir):
        os.makedirs(right_save_dir)

    left_list, right_list = image_lists[0], image_lists[1]
    cv2.imwrite('{}/{}_0.png'.format(left_save_dir,
                                     time.strftime('left_%y-%m-%d-%H-%M-%S-',
                                                   time.localtime(time.time())) + now_string[now_string.rfind('.') + 1:]), left_list[0])
    cv2.imwrite('{}/{}_45.png'.format(left_save_dir,
                                      time.strftime('left_%y-%m-%d-%H-%M-%S-',
                                                    time.localtime(time.time())) + now_string[now_string.rfind('.') + 1:]), left_list[1])
    cv2.imwrite('{}/{}_90.png'.format(left_save_dir,
                                      time.strftime('left_%y-%m-%d-%H-%M-%S-',
                                                    time.localtime(time.time())) + now_string[now_string.rfind('.') + 1:]), left_list[2])
    cv2.imwrite('{}/{}_135.png'.format(left_save_dir,
                                       time.strftime('left_%y-%m-%d-%H-%M-%S-',
                                                     time.localtime(time.time())) + now_string[now_string.rfind('.') + 1:]), left_list[3])
    # right
    cv2.imwrite('{}/{}_0.png'.format(right_save_dir,
                                     time.strftime('right_%y-%m-%d-%H-%M-%S-',
                                                   time.localtime(time.time())) + now_string[now_string.rfind('.') + 1:]), right_list[0])
    cv2.imwrite('{}/{}_45.png'.format(right_save_dir,
                                      time.strftime('right_%y-%m-%d-%H-%M-%S-',
                                                    time.localtime(time.time())) + now_string[now_string.rfind('.') + 1:]), right_list[1])
    cv2.imwrite('{}/{}_90.png'.format(right_save_dir,
                                      time.strftime('right_%y-%m-%d-%H-%M-%S-',
                                                    time.localtime(time.time())) + now_string[now_string.rfind('.') + 1:]), right_list[2])
    cv2.imwrite('{}/{}_135.png'.format(right_save_dir,
                                       time.strftime('right_%y-%m-%d-%H-%M-%S-',
                                                     time.localtime(time.time())) + now_string[now_string.rfind('.') + 1:]), right_list[3])

    safe_print("image save in {}/{} at {}".format(left_save_dir, right_save_dir, now_string))


def safe_print(*args, **kwargs):
    with threading.Lock():
        print(*args, **kwargs)


def get_left_device_buffer(device):
    global left_images
    global isQuit
    with device.start_stream(10):
        while True:
            buffer = device.get_buffer()
            buffer_array = np.ctypeslib.as_array(buffer.pdata, (buffer.height, buffer.width, int(buffer.bits_per_pixel / 8))) \
                .reshape(buffer.height, buffer.width, int(buffer.bits_per_pixel / 8))
            left_images = get_RGB8_image(buffer_array)
            if isQuit:
                device.requeue_buffer(buffer)
                break
            device.requeue_buffer(buffer)
    device.stop_stream()


def get_right_device_buffer(device):
    global right_images
    global isQuit
    with device.start_stream(10):
        while True:
            buffer = device.get_buffer()
            buffer_array = np.ctypeslib.as_array(buffer.pdata, (buffer.height, buffer.width, int(buffer.bits_per_pixel / 8))) \
                .reshape(buffer.height, buffer.width, int(buffer.bits_per_pixel / 8))
            right_images = get_RGB8_image(buffer_array)
            if isQuit:
                device.requeue_buffer(buffer)
                break
            device.requeue_buffer(buffer)
    device.stop_stream()


def example_entry_point():
    # Create devices
    global isQuit
    serialNumber_list = []
    save_dir = ["tri050S34(left)", "tri050S36(right)"]

    devices = create_devices_with_tries()
    for device in devices:
        configure_some_nodes(device)
        serialNumber_list.append(device.nodemap['DeviceSerialNumber'].value)
    serialNumber_list_sorted = sorted(serialNumber_list)
    if serialNumber_list[0] != serialNumber_list_sorted[0]:
        devices = devices[::-1]
    left_device, right_device = devices[0], devices[1]
    left_thread = threading.Thread(target=get_left_device_buffer, args=(left_device,))
    right_thread = threading.Thread(target=get_right_device_buffer, args=(right_device,))
    left_thread.start()
    right_thread.start()

    time.sleep(5)
    while True:
        left_show_image = cv2.resize(get_cat_image(left_images), (612, 512))
        right_show_image = cv2.resize(get_cat_image(right_images), (612, 512))
        border = np.multiply(np.ones((512, 10, 3), dtype=np.uint8), 255)
        show_image = np.concatenate((left_show_image, border, right_show_image), axis=1)
        cv2.imshow("Left || Right", show_image)
        key = cv2.waitKey(1)
        if key & 0xFF == ord("q"):
            cv2.destroyWindow("Left || Right")
            isQuit = True
            left_thread.join()
            right_thread.join()
            break
        elif key & 0xFF == ord("s"):
            image_lists = [left_images, right_images]
            save_images(image_lists, save_dir)

    system.destroy_device()


if __name__ == '__main__':
    print('\nAcquisition started via multi device\n')
    example_entry_point()
    print('\nAcquisition finished successfully')

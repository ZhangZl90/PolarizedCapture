# @Author:ZhangZl
# @Date:30/11/2021
import datetime
import os
import threading
import time

import cv2
import numpy as np
from arena_api import enums
from arena_api.buffer import BufferFactory
from arena_api.system import system


def create_devices_with_tries():
    """
    This function waits for the user to connect a device before raising
    an exception
    """

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


def get_cat_image(buffer_array):
    image_d0 = cv2.cvtColor(buffer_array[:, :, 0], cv2.COLOR_BayerRG2RGB)
    cv2.putText(image_d0, "degree 0", (10, 45), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1.5, thickness=2, color=(0, 0, 255))
    image_d45 = cv2.cvtColor(buffer_array[:, :, 1], cv2.COLOR_BayerRG2RGB)
    cv2.putText(image_d45, "degree 45", (10, 45), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1.5, thickness=2, color=(0, 0, 255))
    image_d90 = cv2.cvtColor(buffer_array[:, :, 2], cv2.COLOR_BayerRG2RGB)
    cv2.putText(image_d90, "degree 90", (10, 45), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1.5, thickness=2, color=(0, 0, 255))
    image_d135 = cv2.cvtColor(buffer_array[:, :, 3], cv2.COLOR_BayerRG2RGB)
    cv2.putText(image_d135, "degree 135", (10, 45), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1.5, thickness=2, color=(0, 0, 255))
    img1 = np.concatenate((image_d0, image_d45), axis=1)
    img2 = np.concatenate((image_d90, image_d135), axis=1)
    img = np.concatenate((img1, img2), axis=0)
    return img


def convert_BayerRG8_to_RGB8(buffer):
    return BufferFactory.convert(buffer, new_pixel_format=enums.PixelFormat.RGB8)


def save_images(buffer_array, save_dir):
    now = datetime.datetime.now()
    save_dir = f'''{save_dir}/{now.year}-{now.month}-{now.day}'''
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    a = str(now)
    image_d0 = cv2.cvtColor(buffer_array[:, :, 0], cv2.COLOR_BayerRG2RGB)
    cv2.imwrite('{}/{}_0.png'.format(save_dir,
                                     time.strftime('%y-%m-%d-%H-%M-%S-',
                                                   time.localtime(time.time())) + a[a.rfind('.') + 1:]), image_d0)
    image_d45 = cv2.cvtColor(buffer_array[:, :, 1], cv2.COLOR_BayerRG2RGB)
    cv2.imwrite('{}/{}_45.png'.format(save_dir,
                                      time.strftime('%y-%m-%d-%H-%M-%S-',
                                                    time.localtime(time.time())) + a[a.rfind('.') + 1:]), image_d45)
    image_d90 = cv2.cvtColor(buffer_array[:, :, 2], cv2.COLOR_BayerRG2RGB)
    cv2.imwrite('{}/{}_90.png'.format(save_dir,
                                      time.strftime('%y-%m-%d-%H-%M-%S-',
                                                    time.localtime(time.time())) + a[a.rfind('.') + 1:]), image_d90)
    image_d135 = cv2.cvtColor(buffer_array[:, :, 3], cv2.COLOR_BayerRG2RGB)
    cv2.imwrite('{}/{}_135.png'.format(save_dir,
                                       time.strftime('%y-%m-%d-%H-%M-%S-',
                                                     time.localtime(time.time())) + a[a.rfind('.') + 1:]), image_d135)
    safe_print("image save in {} at {}".format(save_dir, a))


def safe_print(*args, **kwargs):
    """
    This function ensures resource access is locked to a single thread
    """
    with threading.Lock():
        print(*args, **kwargs)


def get_single_device_buffer(device):
    configure_some_nodes(device)
    thread_id = f'''{device.nodemap['DeviceModelName'].value}''' \
                f'''-{device.nodemap['DeviceSerialNumber'].value} |'''
    save_dir = f'''{thread_id[:-2]}'''

    with device.start_stream(10):
        while True:
            buffer = device.get_buffer()
            buffer_array = np.ctypeslib.as_array(buffer.pdata, (buffer.height, buffer.width, int(buffer.bits_per_pixel / 8))) \
                .reshape(buffer.height, buffer.width, int(buffer.bits_per_pixel / 8))
            img = get_cat_image(buffer_array)
            cv2.imshow(f'''Win-{thread_id[:-2]}''', cv2.resize(img, (612, 512)))
            key = cv2.waitKey(1)
            if key & 0xFF == ord("q"):
                device.requeue_buffer(buffer)
                cv2.destroyWindow(f'''Win-{thread_id[:-2]}''')
                break
            elif key & 0xFF == ord("s"):
                # print(f'''frame id {buffer.frame_id}''')
                save_images(buffer_array, save_dir)
            device.requeue_buffer(buffer)

    device.stop_stream()
    # system.destroy_device()
    safe_print(f'''Shutdown devices {thread_id[:-2]}''')


if __name__ == '__main__':
    print('\nAcquisition started via single device\n')
    devices = create_devices_with_tries()
    device = devices[0]
    print(f'Device used in the example:\n\t{device}')
    get_single_device_buffer(device)
    print('\nAcquisition finished successfully')

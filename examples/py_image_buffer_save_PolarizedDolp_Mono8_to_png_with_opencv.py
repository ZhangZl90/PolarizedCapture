# -----------------------------------------------------------------------------
# Copyright (c) 2021, Lucid Vision Labs, Inc.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------

import os
import time
from pathlib import Path

import cv2  # pip install opencv-python
import numpy as np  # pip install numpy

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
                f'Try {tries+1} of {tries_max}: waiting for {sleep_time_secs} '
                f'secs for a device to be connected!')
            for sec_count in range(sleep_time_secs):
                time.sleep(1)
                print(f'{sec_count + 1 } seconds passed ',
                      '.' * sec_count, end='\r')
            tries += 1
        else:
            print(f'Created {len(devices)} device(s)')
            return devices
    else:
        raise Exception(f'No device found! Please connect a device and run '
                        f'the example again.')


def example_entry_point():

    # Create a device
    devices = create_devices_with_tries()
    device = devices[0]
    print(f'Device used in the example:\n\t{device}')

    # Get device stream nodemap
    tl_stream_nodemap = device.tl_stream_nodemap

    # Enable stream auto negotiate packet size
    tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True

    # Enable stream packet resend
    tl_stream_nodemap['StreamPacketResendEnable'].value = True

    # Get nodes ---------------------------------------------------------------
    nodes = device.nodemap.get_node(['Width', 'Height', 'PixelFormat'])

    # Nodes
    print('Setting Width to its maximum value')
    nodes['Width'].value = nodes['Width'].max

    print('Setting Height to its maximum value')
    height = nodes['Height']
    height.value = height.max

    # Set pixel format to PolarizedDolp_Mono8
    pixel_format_name = 'PolarizedDolp_Mono8'
    print(f'Setting Pixel Format to {pixel_format_name}')
    nodes['PixelFormat'].value = pixel_format_name

    # Grab and save an image buffer -------------------------------------------
    print('Starting stream')
    with device.start_stream(1):
        print('Grabbing an image buffer')
        image_buffer = device.get_buffer()  # Optional args

        print(f' Width X Height = '
              f'{image_buffer.width} x {image_buffer.height}')

        # np.ctypeslib.as_array() detects that Buffer.pdata is (uint8, c_ubyte)
        # type so it interprets each byte as an element.
        # For 16Bit images Buffer.pdata must be cast to (uint16, c_ushort)
        # using ctypes.cast(). After casting, np.ctypeslib.as_array() can
        # interpret every two bytes as one array element (a pixel).
        print('Converting image buffer to a numpy array')
        nparray_reshaped = np.ctypeslib.as_array(image_buffer.pdata,
                                                 (image_buffer.height,
                                                  image_buffer.width))

        # Saving --------------------------------------------------------------
        print('Saving image')

        # RAW
        png_raw_name = f'from_{pixel_format_name}_raw_to_png_with_opencv.png'
        cv2.imwrite(png_raw_name, nparray_reshaped)
        print(f'Saved image path is: {Path(os.getcwd()) / png_raw_name}')

        # HSV
        png_hsv_name = f'from_{pixel_format_name}_hsv_to_png_with_opencv.png'
        cm_nparray = cv2.applyColorMap(nparray_reshaped, cv2.COLORMAP_HSV)
        cv2.imwrite(png_hsv_name, cm_nparray)
        print(f'Saved image path is: {Path(os.getcwd()) / png_hsv_name}')

        device.requeue_buffer(image_buffer)


if __name__ == '__main__':
    print('\nWARNING:\nTHIS EXAMPLE MIGHT CHANGE THE DEVICE(S) SETTINGS!')
    print('\nExample started\n')
    example_entry_point()
    print('\nExample finished successfully')

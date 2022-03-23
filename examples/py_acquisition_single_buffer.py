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


# Buffer contains image data or image with chunkdata

def get_one_image_buffer(device):
    # Starting the stream allocates buffers, which can be passed in as
    # an argument (default: 10), and begins filling them with data.
    # Buffers must later be requeued to avoid memory leaks.
    with device.start_stream():
        print(f'Stream started with 10 buffers')

        # 'Device.get_buffer()' with no arguments returns only one buffer
        print('\tGet one buffer')
        buffer = device.get_buffer()
        # Print some info about the image in the buffer
        print(f'\t\tbuffer received   | '
              f'Width = {buffer.width} pxl, '
              f'Height = {buffer.height} pxl, '
              f'Pixel Format = {buffer.pixel_format.name}')
        print("Buffer")
        buffer_array = np.ctypeslib.as_array(buffer.pdata, (buffer.height, buffer.width, int(buffer.bits_per_pixel / 8))) \
            .reshape(buffer.height, buffer.width, int(buffer.bits_per_pixel / 8))
        print(buffer_array.shape)
        # cv2.imwrite("buffer.png", buffer_array)
        # cv2.imshow("buffer", buffer_array)
        array_0 = cv2.cvtColor(buffer_array[:, :, 3], cv2.COLOR_BayerRG2RGB)
        cv2.imshow("Win-90", array_0)
        cv2.imwrite('135.png', array_0)
        cv2.waitKey(0)

        print("Buffer RGB8")
        buffer_RGB8 = BufferFactory.convert(buffer, new_pixel_format=enums.PixelFormat.RGB8)
        buffer_RGB8_array = np.ctypeslib.as_array(buffer_RGB8.pdata, (buffer_RGB8.height, buffer_RGB8.width, int(buffer_RGB8.bits_per_pixel / 8))) \
            .reshape(buffer_RGB8.height, buffer_RGB8.width, int(buffer_RGB8.bits_per_pixel / 8))
        print(buffer_RGB8_array.shape)
        cv2.imwrite("buffer_RGB8.png", buffer_RGB8_array)
        # cv2.imshow("buffer_RGB8", buffer_RGB8_array)
        print("buffer BGR8")
        buffer_BGR8 = BufferFactory.convert(buffer, new_pixel_format=enums.PixelFormat.BGR8)
        buffer_BGR8_array = np.ctypeslib.as_array(buffer_BGR8.pdata, (buffer_BGR8.height, buffer_BGR8.width, int(buffer_BGR8.bits_per_pixel / 8))) \
            .reshape(buffer_BGR8.height, buffer_BGR8.width, int(buffer_BGR8.bits_per_pixel / 8))
        print(buffer_BGR8_array.shape)
        cv2.imwrite("buffer_BGR8.png", buffer_BGR8_array)
        img_90 = buffer_BGR8_array[::2, ::2, :]
        img_90_2 = img_90[::2, ::2, :]
        cv2.imwrite("buffer_BGR8_90.png", img_90)
        cv2.imwrite("buffer_BGR8_90_2.png", img_90_2)
        # cv2.imshow("buffer_BGR8", buffer_BGR8_array)
        BufferFactory.destroy(buffer_RGB8)
        BufferFactory.destroy(buffer_BGR8)
        # Requeue the image buffer
        device.requeue_buffer(buffer)
        # cv2.waitKey(0)


def example_entry_point():
    # Create a device
    devices = create_devices_with_tries()
    device = devices[0]
    print(f'Device used in the example:\n\t{device}')

    # Set features before streaming.-------------------------------------------
    print('Getting \'Width\' and \'Height\' Nodes')
    nodes = device.nodemap.get_node(['Width', 'Height', 'PixelFormat'])

    # Set width and Height to their max values
    print('Setting \'Width\' and \'Height\' Nodes value to their '
          'max values')
    nodes['Width'].value = nodes['Width'].max
    nodes['Height'].value = nodes['Height'].max
    nodes['PixelFormat'].value = 'PolarizedAngles_0d_45d_90d_135d_BayerRG8'

    # Grab images -------------------------------------------------------------
    get_one_image_buffer(device)

    # Clean up ----------------------------------------------------------------

    # Stop stream and destroy device. This call is optional and will
    # automatically be called for any remaining devices when the system
    # module is unloading.
    system.destroy_device()
    print('Destroyed all created devices')


if __name__ == '__main__':
    print('\nWARNING:\nTHIS EXAMPLE MIGHT CHANGE THE DEVICE(S) SETTINGS!')
    print('\nExample started\n')
    example_entry_point()
    print('\nExample finished successfully')

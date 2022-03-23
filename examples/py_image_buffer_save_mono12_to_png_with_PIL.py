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

import ctypes  # ctypes.cast(), ctypes.POINTER(), ctypes.c_ushort
import os  # os.getcwd()
import time
from pathlib import Path

import numpy as np  # pip install numpy
from PIL import Image as PIL_Image  # pip install Pillow

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

    # Set pixel format to Mono12, most cameras should support this pixel format
    pixel_format_name = 'Mono12'
    print(f'Setting Pixel Format to {pixel_format_name}')
    nodes['PixelFormat'].value = pixel_format_name

    # Grab and save an image buffer -------------------------------------------
    print('Starting stream')
    with device.start_stream(1):

        # Optional args
        print('Grabbing an image buffer')
        image_buffer = device.get_buffer()

        print(f' Width X Height = '
              f'{image_buffer.width} x {image_buffer.height}')

        # To save an image Pillow needs an array that is shaped to
        # (height, width). In order to obtain such an array we use numpy
        # library
        print('Converting image buffer to a numpy array')

        # Buffer.pdata is a (uint8, ctypes.c_ubyte) type
        # Buffer.data is a list of elements each represents one byte.
        # Since Mono12 uses 16Bits (2 bytes), It is easier to user Buffer.pdata
        # over Buffer.data. Buffer.pdata must be cast to (uint16, c_ushort)
        # so every element in the array would represent one pixel.
        pdata_as16 = ctypes.cast(image_buffer.pdata,
                                 ctypes.POINTER(ctypes.c_ushort))
        nparray_reshaped = np.ctypeslib.as_array(
            pdata_as16,
            (image_buffer.height, image_buffer.width))

        # Saving --------------------------------------------------------------
        print('Saving image')

        png_name = f'from_{pixel_format_name}_to_png_with_pil.png'

        # ---------------------------------------------------------------------
        # These steps are due to a bug in Pillow saving 16bits png images
        # more : https://github.com/python-pillow/Pillow/issues/2970

        nparray_reshaped_as_bytes = nparray_reshaped.tobytes()
        png_array = PIL_Image.new('I', nparray_reshaped.T.shape)
        png_array.frombytes(nparray_reshaped_as_bytes, 'raw', 'I;16')
        # ---------------------------------------------------------------------
        png_array.save(png_name)
        print(f'Saved image path is: {Path(os.getcwd()) / png_name }')

        device.requeue_buffer(image_buffer)

    # Clean up ---------------------------------------------------------------

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

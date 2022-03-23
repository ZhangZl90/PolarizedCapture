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
from tkinter import *

# pip3 install numpy
import numpy as np
# pip3 install pillow
from PIL import Image as PIL_Image
from PIL import ImageTk as PIL_ImageTk

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


def configure_some_nodes(nodemap, stream_nodemap):

    # Enable stream auto negotiate packet size
    stream_nodemap['StreamAutoNegotiatePacketSize'].value = True

    # Enable stream packet resend
    stream_nodemap['StreamPacketResendEnable'].value = True

    # Width and height --------------------------------------------------------
    print('Getting \'Width\', \'Height\', and \'PixelFormat\' Nodes')
    nodes = nodemap.get_node(['Width', 'Height', 'PixelFormat'])

    # Set width and height to their max values
    print('Setting \'Width\' and \'Height\' Nodes value to their '
          'max values')
    nodes['Width'].value = nodes['Width'].max
    nodes['Height'].value = nodes['Height'].max

    # Pixel format ------------------------------------------------------------
    new_pixel_format = 'BayerRG8'
    print(f'Setting \'PixelFormat\' to \'{new_pixel_format}\'')
    nodes['PixelFormat'].value = new_pixel_format


def convert_buffer_to_BGR8(buffer):

    # Optional:
    # The pixel format can be checked to a void conversion if possible:
    # Code:
    '''
    if buffer.pixel_format == enums.PixelFormat.BGR8:
        return buffer
    '''
    print('Converting image buffer pixel format to BGR8 ')
    return BufferFactory.convert(buffer, enums.PixelFormat.BGR8)


def example_entry_point():
    """
     Main factors to display images from PolarizedCapture to Tkinter widget

     Pixel Format
     ------------
     Buffer pixel arrangement should match the BGR8 arrangement.
     To get BGR8 arrangement in a buffer from the device:
       - set device to deliver BGR8 buffers before streaming by setting
             'PixelFormat' node to BGR8. This is a more efficient way because
             there is no need to convert the buffer afterward.
       - Or get any convertible pixel format from the device then convert it to
             BGR8 pixel formats using BufferFactory.convert().

     TK image
     --------
     Tkinter can only display images but cannot create them. The example shows
     how to create Tkinter readable images via Pillow library.

     Multi Dimensional array
     -----------------------
     Pillow library can create Tkinter readable images using PIL.ImageTk
     class. However the data list must be a 3 dimensional array. Therefore,
     Numpy library is used to provides a way to reshape a 1D list to
     a 3D array.
    """

    # Create a device
    devices = create_devices_with_tries()
    device = devices[0]
    print(f'Device used in the example:\n\t{device}')

    # Set features before streaming
    configure_some_nodes(device.nodemap, device.tl_stream_nodemap)

    # Grab a single buffer
    # 'Device.start_stream()' has a default argument of 10 buffers to fill with
    # image data
    buffer_BGR8 = None
    with device.start_stream(1):
        print(f'Stream started with 1 buffer')

        # 'Device.get_buffer()' with no arguments returns only one buffer
        print('\tGetting one buffer')
        device_buffer = device.get_buffer()

        # Convert to tkinter recognizable pixel format
        buffer_BGR8 = convert_buffer_to_BGR8(device_buffer)

        # Requeue to release buffer memory
        print('Requeuing device buffer')
        device.requeue_buffer(device_buffer)

    # Create a Numpy array to pass to PIL.Image
    print('Creating 3 dimensional Numpy array')
    buffer_BGR8_data = buffer_BGR8.data
    buffer_BGR8_width = buffer_BGR8.width
    buffer_BGR8_height = buffer_BGR8.height
    buffer_BGR8_bytes_per_pixel = int(
        len(buffer_BGR8_data)/(buffer_BGR8_width * buffer_BGR8_height))
    np_array = np.asarray(buffer_BGR8_data, dtype=np.uint8)
    np_array = np_array.reshape(buffer_BGR8_height,
                                buffer_BGR8_width,
                                buffer_BGR8_bytes_per_pixel)

    print('Creating \'PIL.Image\' instance from Numpy array')
    pil_image = PIL_Image.fromarray(np_array)
    pil_image.save("./BGR8.png")

    print('Creating a Tkinter readable image from \'PIL.Image\' instance')
    root = Tk()
    pil_imagetk_photoimage = PIL_ImageTk.PhotoImage(pil_image)

    label = Label(root, image=pil_imagetk_photoimage)
    label.pack()
    root.mainloop()

    # The buffer factory gives a converted copy of the device buffer, so
    # destroy the image copy to prevent memory leaks
    BufferFactory.destroy(buffer_BGR8)

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

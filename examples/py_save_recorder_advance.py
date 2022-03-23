
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


import queue
import threading
import time

from arena_api.__future__.save import Recorder
from arena_api.buffer import BufferFactory
from arena_api.enums import PixelFormat
from arena_api.system import system


def create_devices_with_tries():
    """
    just a function to let example users know that a device is needed and
    gives them a chance to connected a device instead of raising an exception
    """
    tries = 0
    tries_max = 5
    sleep_time_secs = 10
    while tries < tries_max:  # waits for devices for a min
        devices = system.create_device()
        if not devices:
            print(
                f'try {tries+1} of {tries_max}: waiting for {sleep_time_secs} '
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

    # Get connected devices ---------------------------------------------------

    # create_device function with no arguments would create a list of
    # device objects from all connected devices
    devices = create_devices_with_tries()
    if not devices:
        return

    device = devices[0]
    nodemap = device.nodemap
    tl_stream_nodemap = device.tl_stream_nodemap
    print(f'Device used in the example:\n\t{device}')    

    # Enable stream auto negotiate packet size
    tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True

    # Enable stream packet resend
    tl_stream_nodemap['StreamPacketResendEnable'].value = True

    # Set node values ---------------------------------------------------------

    # set width and height to max values might make the video frame rate low
    # The larger the height of the buffer the lower the fps
    width_node = nodemap['Width']
    width = nodemap['Width'].max // 3
    # get a value that aligned with node increments
    while width % width_node.inc:
        width -= 1
    nodemap['Width'].value = width

    height_node = nodemap['Height']
    height = nodemap['Height'].max // 3
    # get a value that aligned with node increments
    while height % height_node.inc:
        height -= 1
    nodemap['Height'].value = height

    # if the images from the device are already in the pixel format expected
    # by the recorder then no need to convert the received buffers. This
    # would result in a better performance
    #   ``nodemap['PixelFormat'].value = PixelFormat.BGR8``
    # HOWEVER
    # For demonstration lets change pixel format so we can show where the
    # recorder knows how to convert the buffers
    nodemap['PixelFormat'].value = PixelFormat.Mono8

    # For performance ---------------------------------------------------------

    # make sure the device sends images continuously
    device.nodemap['AcquisitionMode'].value = 'Continuous'

    # automate the calculation of max FPS whenever the device settings change
    nodemap['AcquisitionFrameRateEnable'].value = True

    # set FPS node to max FPS which was set to be automatically calculated
    # base on current device settings
    nodemap['AcquisitionFrameRate'].value = nodemap['AcquisitionFrameRate'].max

    # max FPS according to the current settings
    nodemap['DeviceStreamChannelPacketSize'].value = nodemap['DeviceStreamChannelPacketSize'].max

    # Start stream ------------------------------------------------------------
    total_images = 100

    with device.start_stream(1):
        print('Stream started')

        # recorder -------------------------------------------------------------

        # creation / configuration -------------------------
        # The recorder, takes width, height, and frames per seconds.
        # These argument can be deferred until Recorder.open is called.
        #
        # NOTE:
        # `threaded` parameter, None by default, would allow the call to
        # `recorder.append()` to return right a way after putting the
        # buffer in a share queue to be processed on separate thread.
        # It might be faster but it means calling `recorder.close()`
        # would have to wait for all appended buffers to be added to the
        # video file.
        recorder = Recorder(nodemap['Width'].value,
                            nodemap['Height'].value,
                            nodemap['AcquisitionFrameRate'].value)

        # TODO might want to move to constructor
        # codec expects a tuple that contains
        #  (video_coding, expected_buffer_pixelformat, file_extension)
        # the recorder will convert the buffers to the pixelformat in
        # the codec. In this case it will convert Mono8 buffer to BGR8 then
        # append them to the video. In fact this conversion happens in the
        # background. Here just showing where the recorder knows what format
        # to convert to
        recorder.codec = ('h264', 'mp4', 'bgr8')  # order does not matter

        # set video name -----------------------------------
        recorder.pattern = 'My_vid<count>.mp4'

        # recorder settings can not be changed after open is called util
        # Recorder.close() is called

        # - After recorder.open() add image to the open recorder by
        # appending buffers to the video. the recorder expects buffers to be
        # in the pixel format specified in Recorder.codec therefor,
        # BufferFactory.convert() is used
        # - The default name for the video is 'video<count>.mp4' where count
        # is a pre-defined tag that gets updated every time open()
        # is called. More custom tags can be added using
        # Recorder.register_tag() function
        recorder.open()
        print('recorder opened')

        # Get buffers --------------------------------------

        for itr_count in range(total_images):

            buffer = device.get_buffer()

            # append to the open recorder
            # this will append the buffer to the video after converting the
            # buffer to the format in recorder.codec
            recorder.append(buffer)

            # requeue buffer back to device
            device.requeue_buffer(buffer)

        # finalize -----------------------------------------

        # must be called after finish adding the buffers
        recorder.close()
        print('recorder closed')

        # video path
        print(f'video saved {recorder.saved_videos[-1]}')

        # approximate length of the video
        video_length_in_secs = total_images / \
            nodemap['AcquisitionFrameRate'].value

        print(f'video length ~= {video_length_in_secs: .3} seconds')

    # device.stop_stream() is automatically called at the end of the
    # context manger scope

    # clean up ----------------------------------------------------------------

    # This function call with no arguments will destroy all of the
    # created devices. Having this call here is optional, if it is not
    # here it will be called automatically when the system module is unloading.
    system.destroy_device()
    print('Destroyed all created devices')


if __name__ == '__main__':
    print('WARNING:\nTHIS EXAMPLE MIGHT CHANGE THE DEVICE(S) SETTINGS!')
    print('Example started')
    example_entry_point()
    print('Example finished successfully')

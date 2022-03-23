
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

from arena_api.__future__.save import Recorder
from arena_api.buffer import BufferFactory
from arena_api.enums import PixelFormat
from arena_api.system import system


def create_devices_with_tries():
    """
    just a function to let example users know that a device is needed and
    gives them a chance to connected a device instead of rasing an exception
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
        print(f'No device found! Please connect a device and run the '
              f'example again.')
        return


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
    width = nodemap['Width'].max

    height_node = nodemap['Height']
    height = nodemap['Height'].max

    # if the images from the device are already in the format expected by the
    # recorder then no need to convert received buffers which results in better
    # performance
    nodemap['PixelFormat'].value = PixelFormat.PolarizedAngles_0d_45d_90d_135d_BayerRG8

    # start stream ------------------------------------------------------------

    with device.start_stream(100):
        print('Stream started')

        # create a recorder
        # The recorder, takes width, height, and frames per seconds.
        # These argument can be deferred until Recorder.open is called
        recorder = Recorder(nodemap['Width'].value,
                            nodemap['Height'].value,
                            nodemap['AcquisitionFrameRate'].value)
        print('fps',  nodemap['AcquisitionFrameRate'].value)

        # TODO might want to move to constructor
        recorder.codec = ('h264', 'mp4', 'bgr8')  # order does not matter

        # recorder settings can not be changed after open is called util
        # close is called
        recorder.open()
        print('recorder opened')

        TOTAL_IMAGES = 100
        for count in range(TOTAL_IMAGES):
            buffer = device.get_buffer()
            print(f'Image buffer received')

            # - After recorder.open() add image to the open recorder stream by
            # appending buffers to the video.
            #  - The buffers are already BGR8, because we set 'PixelFormat'
            #  node to 'BGR8', so no need to convert buffers using
            # BufferFactory.convert() from PolarizedCapture.buffer

            #  - default name for the video is 'video<count>.mp4' where count
            # is a pre-defined tag that gets updated every time open()
            # is called. More custom tags can be added using
            # Recorder.register_tag() function
            recorder.append(buffer)
            print(f'Image buffer {count} appended to video')

            device.requeue_buffer(buffer)
            print(f'Image buffer requeued')

        recorder.close()
        print('recorder closed')
        print(f'video saved {recorder.saved_videos[-1]}')

        video_length_in_secs = (TOTAL_IMAGES /
                                nodemap['AcquisitionFrameRate'].value)
        print(f'video length is {video_length_in_secs} seconds')

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

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
from datetime import datetime

from arena_api.__future__.save import Writer
from arena_api.system import system


def time_update_function():
    """
    This function will act like a generator. 
    every time it is triggered would return the time as str in the
    format shown
    """
    while True:
        now = datetime.now()
        yield now.strftime('%H_%M_%S_%f')


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
                f'try {tries + 1} of {tries_max}: waiting for {sleep_time_secs} '
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
    tl_stream_nodemap = device.tl_stream_nodemap
    print(f'Device used in the example:\n\t{device}')

    # Enable stream auto negotiate packet size
    tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True

    # Enable stream packet resend
    tl_stream_nodemap['StreamPacketResendEnable'].value = True

    # just to have a viewable image
    print('Setting \'Width\' and \'Height\' Nodes value to their '
          'max values')
    device.nodemap['Width'].value = device.nodemap['Width'].max
    device.nodemap['Height'].value = device.nodemap['Height'].max
    device.nodemap['PixelFormat'].value = "PolarizeMono8"

    # by default start_stream() has default argument of 10 which
    # means 10 buffers can be filled with images or chunkdata before having to
    # call device.requeue_buffer() on them for reuse.
    with device.start_stream():
        print('Stream started')

        # create an image writer
        # The writer, optionally, can take width, height, and bits per pixel
        # of the image(s) it would save. if these arguments are not passed
        # at run time, the first buffer passed to the Writer.save()
        # function will configure the writer to the arguments buffer's width,
        # height, and bits per pixel
        writer = Writer()

        # add a tag to use in the image name
        # by default the tag 'count' is defined for the user (can be
        # overwritten). A generator or a generator like function to be called
        # when new image saved evaluate its new name
        time_update_generator_from_func = time_update_function()
        writer.register_tag(name='time',
                            generator=time_update_generator_from_func)

        # set image name pattern
        # default name for the image is 'image_<count>.jpg' where count
        # is a pre-defined tag that gets updated every time a buffer image
        # is saved.
        #
        # ** Note: **
        #   all tags in pattern must be registered before
        #   assigning the pattern to writer.pattern
        #
        writer.pattern = 'all_images\my_image_<count>_at_<time>.jpg'

        for image_count in range(100):
            buffer = device.get_buffer()
            print(f'Image buffer {image_count} received')

            # Let assume that one buffer should be saved with different name.
            # set choose the condition then pass the name to save. The name
            # will be used only for this save call and the future calls
            # save() would use the pattern unless another name is passed.
            if buffer.is_incomplete:
                # the case here that image would saved twice. One with the
                # apttern and the second copy by this condition
                writer.save(buffer, f'bad\I_AM_INCOMPLETE_{image_count}.jpg')
                print(f'Image saved {writer.saved_images[-1]}')
            else:
                # save the image with the pattern defined by writer.pattern
                writer.save(buffer)
                print(f'Image saved {writer.saved_images[-1]}')

            device.requeue_buffer(buffer)
            print(f'Image buffer requeued')

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

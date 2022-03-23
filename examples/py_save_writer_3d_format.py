
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

import sys

from arena_api.__future__.save import Writer
from arena_api.enums import PixelFormat
from arena_api.system import system


def validate_device(device):

    # validate if Scan3dCoordinateSelector node exists.
    # If not, it is (probably) not a Helios Camera running the example
    try:
        scan_3d_operating_mode_node = device. \
            nodemap['Scan3dOperatingMode'].value
    except (KeyError):
        print('Scan3dCoordinateSelector node is not found. \
            Please make sure that Helios device is used for the example.\n')
        sys.exit()


def example_entry_point():

    # Get connected devices ---------------------------------------------------

    # create_device function with no arguments would create a list of
    # device objects from all connected devices
    devices = system.create_device()
    if not len(devices):
        raise Exception(f'No device found!\n'
                        f'Please connect a device and run the example again.')
    print(f'Created {len(devices)} device(s)')

    device = devices[0]

    validate_device(device)

    tl_stream_nodemap = device.tl_stream_nodemap
    print(f'Device used in the example:\n\t{device}')

    # Enable stream auto negotiate packet size
    tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True

    # Enable stream packet resend
    tl_stream_nodemap['StreamPacketResendEnable'].value = True

    # choose a 3d pixel format. here unsigned pixelformat is chosen. the
    # signed pixelformat version of this would have the same name with
    # an 's' at the end
    device.nodemap['PixelFormat'].value = PixelFormat.Coord3D_ABC16

    with device.start_stream():
        print('Stream started')

        buffer = device.get_buffer()
        print(f'Image buffer received')

        # create an image writer
        # The writer, optionally, can take width, height, and bits per pixel
        # of the image(s) it would save. if these arguments are not passed
        # at run time, the first buffer passed to the Writer.save()
        # function will configure the writer to the arguments buffer's width,
        # height, and bits per pixel
        writer = Writer()
        # save function
        # buffer :
        #   buffer to save.
        # pattern :
        #   default name for the image is 'image_<count>.jpg' where count
        #   is a pre-defined tag that gets updated every time a buffer image
        #   is saved. More custom tags can be added using
        #   Writer.register_tag() function
        # kwargs (optional args) ignored if not an .ply image:
        #   - 'filter_points' default is True.
        #       Filters NaN points (A = B = C = -32,678)
        #   - 'is_signed' default is False.
        #       If pixel format is signed for example PixelFormat.Coord3D_A16s
        #       then this arg must be passed to the save function else
        #       the results would not be correct
        #   - 'scale' default is 0.25.
        #   - 'offset_a', 'offset_b' and 'offset_c' default to 0.00
        writer.save(buffer, 'I_AM_A_3D_BECAUSE_OF_MY_EXTENSION.ply')

        print(f'Image saved {writer.saved_images[-1]}')

        device.requeue_buffer(buffer)
        print(f'Image buffer requeued')

        # read the point cloud then display it using one of many packages on
        # pypi. For example:
        #   import open3d
        #   pc_file = open3d.io.read_point_cloud(writer.saved_images[-1])
        #   open3d.visualization.draw_geometries([pc_file])
        #
        # Note:
        # open3d package does not support some
        # os/architerctures (Raspbian for exapmle)

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

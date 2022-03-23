# -----------------------------------------------------------------------------
# Copyright (c) 2020, Lucid Vision Labs, Inc.
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

from arena_api.system import system

# The name of the file to stream features to/from
FILE_NAME = 'all_streamable_features.txt'


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
    """
    Streamables
        This example introduces streamables, which uses files to pass settings
        around between devices. This example writes all streamable features
        from a source device to a file, and then writes them from the file to
        all other  connected devices.

    The example
        (1) reads all streamable features from source device
        (2) writes features to file
        (3) reads features from file
        (4) writes features to destination devices
    """

    # Create a device
    devices = create_devices_with_tries()

    device = devices[0]

    print(f'Save streamable features from \n\t{device} \n'
          f'to a {os.getcwd()}{os.path.sep}{FILE_NAME}\n')

    device.nodemap.write_streamable_node_values_to(FILE_NAME)

    print(
        f'Load streamable features from \n'
        f'{os.getcwd()}{os.path.sep}{FILE_NAME}'
        f' to all connected devices\n')

    for device in devices:

        print(f'Loading to {device} \n')
        device.nodemap.read_streamable_node_values_from(FILE_NAME)

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

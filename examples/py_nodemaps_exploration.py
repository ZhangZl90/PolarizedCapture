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


def explore_nodemap(nodemap, nodemap_name):
    print()
    feature_nodes_names = nodemap.feature_names
    print(f'Nodemap has {len(feature_nodes_names)} feature nodes')

    with open(f'arena_api_node_exploration_{nodemap_name}.txt', 'w') as f:
        for node_name in feature_nodes_names:
            # print to output
            print(nodemap[node_name])
            # print to file
            print(nodemap[node_name], file=f)


def example_entry_point():

    # Create a device
    devices = create_devices_with_tries()
    device = devices[0]
    print(f'Device used in the example:\n\t{device}')

    # Explore nodemaps --------------------------------------------------------
    print('========================')
    print('Exploring Device nodemap')
    print('========================')
    explore_nodemap(device.nodemap, 'device_nodemap')
    print('========================================')
    print('Exploring Transport Layer Device nodemap')
    print('========================================')
    explore_nodemap(device.tl_device_nodemap, 'TL_device_nodemap')
    print('========================================')
    print('Exploring Transport Layer Stream nodemap')
    print('========================================')
    explore_nodemap(device.tl_stream_nodemap, 'TL_stream_nodemap')
    print('===========================================')
    print('Exploring Transport Layer Interface nodemap')
    print('===========================================')
    explore_nodemap(device.tl_interface_nodemap, 'TL_interface_nodemap')
    print('========================================')
    print('Exploring Transport Layer System nodemap')
    print('========================================')
    explore_nodemap(system.tl_system_nodemap, 'TL_system_nodemap')
    print('========================================')

    # Clean up ---------------------------------------------------------------

    # Stop stream and destroy device. This call is optional and will
    # automatically be called for any remaining devices when the system module
    # is unloading.
    system.destroy_device()
    print('Destroyed all created devices')


if __name__ == '__main__':
    print('\nWARNING:\nTHIS EXAMPLE MIGHT CHANGE THE DEVICE(S) SETTINGS!')
    print('\nExample started\n')
    example_entry_point()
    print('\nExample finished successfully')

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

from arena_api.system import system


def my_mac():
    """
    The purpose of this function is to dynamically get the MAC address of a
    device that exists so the example passes.
    This function can be avoided if the user wants to hard code the MAC address
    instead.
    """

    device_infos = system.device_infos
    if len(device_infos) == 0:
        raise BaseException('No device is found!')
    else:
        return device_infos[0]['mac']


def find_device_info_contain_mac(mac_to_find):
    """
    Find a specific mac address in device infos then return that device info
    """

    for device_info in system.device_infos:
        if device_info['mac'] == mac_to_find:
            return device_info
    else:
        raise BaseException(f'No device with MAC Address '
                            f'\'{mac_to_find}\' was found!')


def int_to_mac_address(int_mac):
    """
    Converts int value to MAC address of format XX:XX:XX:XX:XX:XX
    """

    hex_mac = f'{int_mac:012x}'
    str_mac = ':'.join(hex_mac[i:i+2] for i in range(0, len(hex_mac), 2))
    return str_mac


def example_entry_point():

    # This function can be replaced with a mac address string that is known
    # to the user
    mac_to_find = my_mac()
    print(f'\'{mac_to_find}\' is the MAC address to find')

    # Find device with the desired MAC address
    device_info = find_device_info_contain_mac(mac_to_find)
    print(f'\'{mac_to_find}\' device was found')

    print('Creating device from device info')
    devices_list = system.create_device(device_infos=device_info)
    device = devices_list[0]
    print(f'Device created: {device}')

    # Simple verification
    # Read device's MAC address from the device to verify
    device_mac_int = device.nodemap.get_node('GevMACAddress').value
    device_mac = int_to_mac_address(device_mac_int)
    print(f'Device MAC Address = {device_mac}')
    if device_mac != mac_to_find:
        raise BaseException('The wrong device has been created')

    # Clean up ----------------------------------------------------------------

    # Stop stream and destroy device. This call is optional and will
    # automatically be called for any remaining devices when the system
    # module is unloading.
    system.destroy_device(device)
    print('Destroyed created device')


if __name__ == '__main__':
    print('\nWARNING:\nTHIS EXAMPLE MIGHT CHANGE THE DEVICE(S) SETTINGS!')
    print('\nExample started\n')
    example_entry_point()
    print('\nExample finished successfully')

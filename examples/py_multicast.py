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

from arena_api.system import system

# Image timeout
TIMEOUT_MILLISEC = 2000

# Length of time to grab images (sec)
#    Note that the listener must be started while the master is still
#    streaming, and that the listener will not receive any more images
#    once the master stops streaming.
NUM_SECONDS = 20


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

    # Enable multicast
    #    Multicast must be enabled on both the master and listener. A small
    #    number of transport layer features will remain writable even
    #    though a device's access mode might be read-only.
    print('Enable multicast')
    device.tl_stream_nodemap['StreamMulticastEnable'].value = True

    # Prepare settings on master, not on listener
    #    Device features must be set on the master rather than the listener.
    #    This is because the listener is opened with a read-only access mode.
    device_access_status = device.tl_device_nodemap['DeviceAccessStatus'].value

    # Master
    if device_access_status == 'ReadWrite':

        print('Host streaming as "master"')

        # Get node values that will be changed in order to return their values
        # at the end of the example
        acquisition_mode_initial = device.nodemap['AcquisitionMode'].value

        # Set acquisition mode
        print('Set acquisition mode to "Continuous"')

        device.nodemap['AcquisitionMode'].value = 'Continuous'

        # Enable stream auto negotiate packet size
        device.tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True

        # Enable stream packet resend
        device.tl_stream_nodemap['StreamPacketResendEnable'].value = True

    # Listener
    else:
        print('Host streaming as "listener"\n')

    # Get images
    print(f'Getting images for {NUM_SECONDS} seconds')

    # Define start and latest time for timed image acquisition
    start_time = datetime.now()
    latest_time = datetime.now()

    # Start stream
    with device.start_stream():

        # Define image count to detect if all images are not received
        image_count = 0
        unreceived_image_count = 0

        print(f'Stream started')

        while (latest_time - start_time).total_seconds() < NUM_SECONDS:

            # update time
            latest_time = datetime.now()

            try:
                image_count = image_count + 1

                # 'Device.get_buffer()' with no arguments returns
                #  only one buffer
                buffer = device.get_buffer(timeout=TIMEOUT_MILLISEC)

                # Print some info about the image in the buffer
                #   Using the frame ID and timestamp allows for the comparison
                #   of images between multiple hosts.
                print(f'\t\tImage retrieved ('
                      f'frame ID = {buffer.frame_id}, '
                      f'timestamp (ns) = {buffer.timestamp_ns}) and requeue')

            except(TimeoutError):
                print(f'\t\tNo image received')
                unreceived_image_count = unreceived_image_count + 1
                continue

            # Requeue the image buffer
            device.requeue_buffer(buffer)

    if (unreceived_image_count == image_count):
        print(f'\nNo images were received, this can be caused by firewall, vpn settings or firmware\n')
        print(f'Please add python application to firewall exception')

    # Return node to its initial value
    if (device_access_status == "ReadWrite"):
        device.nodemap['AcquisitionMode'].value = acquisition_mode_initial

    # Clean up ----------------------------------------------------------------

    # Stop stream and destroy device. This call is optional and will
    # automatically be called for any remaining devices when the system
    # module is unloading.
    system.destroy_device()
    print('\nDestroyed all created devices')


if __name__ == '__main__':
    print('\nWARNING:\nTHIS EXAMPLE MIGHT CHANGE THE DEVICE(S) SETTINGS!')
    print('\nExample started\n')
    example_entry_point()
    print('\nExample finished successfully')

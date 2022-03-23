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

# Updated in 1.7.0

import time

from arena_api.callback import callback, callback_function
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


# Must have the decorator on the callback function
@callback_function.node.on_update
def print_node_value(node, *args, **kwargs):

    print(f'Message from callback')
    print(f'\'{node.name}\' event has triggered this callback')


def apply_trigger_settings(device):

    # Enable trigger mode before setting the source and selector
    # and before starting the stream. Trigger mode cannot be turned
    # on and off while the device is streaming.

    # Make sure Trigger Mode set to 'Off' after finishing this example
    device.nodemap.get_node('TriggerMode').value = 'On'

    # Set the trigger source to software in order to trigger buffers
    # without the use of any additional hardware.
    # Lines of the GPIO can also be used to trigger.
    device.nodemap.get_node('TriggerSource').value = 'Software'

    device.nodemap.get_node('TriggerSelector').value = 'FrameStart'

    device.tl_stream_nodemap.get_node(
        'StreamBufferHandlingMode').value = 'OldestFirst'


def example_entry_point():

    # Create a device
    devices = create_devices_with_tries()
    device = devices[0]

    # Store nodes' initial values ---------------------------------------------

    # get node values that will be changed in order to return their values at
    # the end of the example
    streamBufferHandlingMode_initial = \
        device.tl_stream_nodemap['StreamBufferHandlingMode'].value
    triggerSource_initial = device.nodemap['TriggerSource'].value
    triggerSelector_initial = device.nodemap['TriggerSelector'].value
    triggerMode_initial = device.nodemap['TriggerMode'].value

    # -------------------------------------------------------------------------

    print(f'Device used in the example:\n\t{device}')

    apply_trigger_settings(device)

    # Initialize events
    # Turn event notification on
    # Select the event type to be notified about
    device.initialize_events()
    device.nodemap.get_node('EventSelector').value = 'ExposureEnd'
    device.nodemap.get_node('EventNotification').value = 'On'

    # Register the callback on the node
    event_node = device.nodemap.get_node('EventExposureEnd')
    handle = callback.register(event_node, print_node_value)
    print(f'Registered \'{print_node_value.__name__}\' function '
          f'on {event_node.name}\' node')
    
    # Get device stream nodemap
    tl_stream_nodemap = device.tl_stream_nodemap

    # Enable stream auto negotiate packet size
    tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True

    # Enable stream packet resend
    tl_stream_nodemap['StreamPacketResendEnable'].value = True

    # Start the stream
    device.start_stream()
    print('Stream started')

    for _ in range(10):

        # Continually check until trigger is armed. Once the trigger is
        # armed, it is ready to be executed.
        while not device.nodemap.get_node('TriggerArmed').value:
            continue

        # Trigger an image buffer manually, since trigger mode is enabled.
        # This triggers the camera to acquire a single image buffer.
        # A buffer is then filled and moved to the output queue, where
        # it will wait to be retrieved.
        # Before the image buffer is sent, the exposure end event will
        # occur. This will happen on every iteration
        device.nodemap.get_node('TriggerSoftware').execute()

        # Wait on the event to process it, invoking the registered callback.
        # The data is created from the event generation, not from waiting
        # on it. If the exposure time is long a Timeout exception may
        # occur unless large timeout value is
        # passed to the 'Device.wait_on_event()'
        device.wait_on_event()

    # Clean up ----------------------------------------------------------------

    # Callbacks must be unregistered and events must be deinitialized
    callback.deregister(handle)
    device.deinitialize_events()

    # Stop stream before destroying device to set nodes back to initial values
    device.stop_stream()

    device.nodemap['TriggerSource'].value = triggerSource_initial
    device.nodemap['TriggerSelector'].value = triggerSelector_initial
    device.nodemap['TriggerMode'].value = triggerMode_initial

    # Destroy device
    #   stop_stream() call is optional and will
    #   automatically be called for any remaining devices when the system
    #   module is unloading.
    system.destroy_device()
    print('Destroyed all created devices')


if __name__ == '__main__':
    print('\nWARNING:\nTHIS EXAMPLE MIGHT CHANGE THE DEVICE(S) SETTINGS!')
    print('\nExample started\n')
    example_entry_point()
    print('\nExample finished successfully')

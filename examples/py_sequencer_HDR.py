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

import os
import time
from pathlib import Path

from arena_api import enums
from arena_api.__future__.save import Writer
from arena_api.system import system

# Note: buffer contains an image with or without chunkdata


def create_devices_with_tries():
    """
    This function waits for the user to connect a device before raising
    an exception
    """

    tries = 0
    tries_max = 6
    sleep_time_secs = 10
    while tries < tries_max:  # Waits for devices
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


def set_sequencer_set(nodemap, set_number, exposure_time, path_next_set,
                      trigger_source):

    # Set Sequencer Set Selector to sequence number
    nodemap['SequencerSetSelector'].value = set_number
    print(f'Updating set {set_number} :')

    # Set Exposure Time to the desired value
    nodemap['SequencerFeatureSelector'].value = 'ExposureTime'
    nodemap['ExposureTime'].value = exposure_time
    print(f'\texposure time value = {exposure_time}')

    # Select the path we want it to follow from this set to the next set. There
    # can be multiple paths so the first path will always be set to 0
    nodemap['SequencerPathSelector'].value = 0

    # Set next state in the sequence, ensure it does not exceed the maximum
    nodemap['SequencerSetNext'].value = path_next_set
    print(f'\tset next            = {path_next_set}')

    # Set Sequencer Trigger Source to Frame Start
    nodemap['SequencerTriggerSource'].value = trigger_source
    print(f'\ttrigger source      = {trigger_source}')

    # Save current state
    # Once all appropriate settings have been configured, make sure to
    # save the state to the sequence. Notice that these settings will be
    # lost when the camera is power-cycled.
    print(f'\tSave sequence set {set_number}')
    nodemap['SequencerSetSave'].execute()


def acquire_and_save_buffers(device):

    # Get width, height, and pixel format nodes
    width_node = device.nodemap['Width']
    height_node = device.nodemap['Height']
    pixelformat_node = device.nodemap['PixelFormat']

    if not width_node.is_readable or \
            not height_node.is_readable or \
            not pixelformat_node.is_readable:
        raise Exception('Width, Height, or PixelFormat node is not readable')

    pixelformat_node.value = 'Mono8'

    # Starting the stream allocates buffers, which can be passed in as
    # an argument (default: 10), and begins filling them with data.
    print('\nStart streaming')
    with device.start_stream(3):

        # Get an image buffer in each set of sequencer
        print('Getting 3 image buffers')

        # Save images
        #   Create an image writer
        #   The writer, optionally, can take width, height, and bits per pixel
        #   of the image(s) it would save. if these arguments are not passed
        #   at run time, the first buffer passed to the Writer.save()
        #   function will configure the writer to the arguments buffer's width,
        #   height, and bits per pixel

        writer = Writer()

        # Run our 3 sets one time
        for count in range(3):
            print(f'\tConverting and saving image {count}')

            # Get image
            buffer = device.get_buffer()

            # Default name for the image is 'image_<count>.jpg' where count
            # is a pre-defined tag that gets updated every time a buffer image
            # is saved. More custom tags can be added using
            # Writer.register_tag() function
            writer.save(buffer)
            print(f'Image saved {writer.saved_images[-1]}')

            # Requeue image buffer
            device.requeue_buffer(buffer)
        print(f'Requeued {count + 1} buffers')

    # Stream stops automatically when the scope of the context manager ends
    print('Stream stopped')


def set_exposure_auto_to_off(nodemap):

    # If Sequencer Configuration Mode is 'On', it makes 'ExposureAuto'
    # a read-only
    if nodemap['SequencerConfigurationMode'].value == 'On':
        print('Turn \'SequencerConfigurationMode\' Off')
        nodemap['SequencerConfigurationMode'].value = 'Off'
        print(f'\t\'SequencerConfigurationMode\' is '
              f'''{nodemap['SequencerConfigurationMode'].value} now''')

    print('Turn \'ExposureAuto\' Off')
    nodemap['ExposureAuto'].value = 'Off'
    print(f'''\t\'ExposureAuto\' is {nodemap['ExposureAuto'].value} now''')


def set_sequencer_configuration_mode_on(nodemap):

    # If Sequencer Mode is 'On', it makes 'SequencerConfigurationMode'
    # a read-only
    if nodemap['SequencerMode'].value == 'On':
        print('Turn \'SequencerMode\' Off')
        nodemap['SequencerMode'].value = 'Off'
        print(
            f'''\t\'SequencerMode\' is {nodemap['SequencerMode'].value} now''')

    print('Turn \'SequencerConfigurationMode\' On')
    nodemap['SequencerConfigurationMode'].value = 'On'
    print(f'\t\'SequencerConfigurationMode\' is '
          f'''{nodemap['SequencerConfigurationMode'].value} now''')


def example_entry_point():

    # Create a device
    devices = create_devices_with_tries()
    device = devices[0]
    print(f'Device used in the example:\n\t{device}')

    nodemap = device.nodemap
    tl_stream_nodemap = device.tl_stream_nodemap

    #  Set up nodes -----------------------------------------------------------

    # Enable stream auto negotiate packet size
    tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True

    # Enable stream packet resend
    tl_stream_nodemap['StreamPacketResendEnable'].value = True    

    # Disable automatic exposure and gain before setting an exposure time.
    # Automatic exposure and gain controls whether they are set manually or
    # automatically by the device. Setting automatic exposure and gain to
    # 'Off' stops the device from automatically updating the exposure time
    # while streaming.
    set_exposure_auto_to_off(nodemap)

    # If 'SequencerMode' is on, turn it off so the sequencer becomes
    # configurable through 'SequencerConfigurationMode'.
    # Put sequencer in configuration mode.
    # Sequencer configuration mode must be on while making changes to
    # the sequencer sets.
    set_sequencer_configuration_mode_on(nodemap)

    # Set up sequencer sets ---------------------------------------------------

    # From device.nodemap['SequencerSetSelector'].max gives the maximum
    # of sequencer sets can be set on the device.

    # Make sure the example works with all devices.
    # Take the smaller value to set a long exposure time of some devices
    exposure_time_long = min(nodemap['ExposureTime'].max, 100000.0)

    print('Set up sequencer sets')
    sets_settings = [
        {
            'set_number': 0,
            'exposure_time': exposure_time_long / 40,
            'path_next_set': 1,
            'trigger_source': 'FrameStart'
        },
        {
            'set_number': 1,
            'exposure_time': exposure_time_long / 20,
            'path_next_set': 2,
            'trigger_source': 'FrameStart'
        },
        {
            'set_number': 2,
            'exposure_time': exposure_time_long,
            'path_next_set': 0,  # Means it goes back to the set in index 0
            'trigger_source': 'FrameStart'
        }
    ]

    for set_settings in sets_settings:
        set_sequencer_set(nodemap, **set_settings)

    # Sets the sequencer starting set to 0
    print('Set stream to start from sequencer set 0')
    nodemap['SequencerSetStart'].value = 0

    # Turn off configuration mode
    print('Turn \'SequencerConfigurationMode\' Off')
    nodemap['SequencerConfigurationMode'].value = 'Off'
    print(f'\t\'SequencerConfigurationMode\' is '
          f'''{nodemap['SequencerConfigurationMode'].value} now''')

    # Turn on sequencer
    #    When sequencer mode is on and the device is streaming it will
    #    follow the sequencer sets according to their saved settings.
    print('Turn \'SequencerMode\' On')
    nodemap['SequencerMode'].value = 'On'
    print(f'''\t\'SequencerMode\' is {nodemap['SequencerMode'].value} now''')

    # Acquire and Save image buffers ------------------------------------------

    # This function will start the stream, acquire a buffer in each set
    # of the sequencer using its corresponding settings, save each buffer
    # and then stop the stream.
    acquire_and_save_buffers(device)

    # Clean up ------------------------------------------------------------

    # Turn sequencer mode off so the device is set to the original settings
    print('Turn \'SequencerMode\' Off')
    nodemap['SequencerMode'].value = 'Off'
    print(f'''\t\'SequencerMode\' is {nodemap['SequencerMode'].value} now''')

    # Destroy all created devices. This call is optional and will
    # automatically be called for any remaining devices when the system module
    # is unloading.
    system.destroy_device()
    print('Destroyed all created devices')


if __name__ == '__main__':
    print('\nWARNING:\nTHIS EXAMPLE MIGHT CHANGE THE DEVICE(S) SETTINGS!')
    print('\nExample started\n')
    example_entry_point()
    print('\nExample finished successfully')

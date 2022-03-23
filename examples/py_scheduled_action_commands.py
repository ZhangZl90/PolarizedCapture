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

"""
 Scheduled Action Commands
    This example introduces scheduling action commands on multiple cameras.
    The device settings are configured to allow each device to trigger a single
    image using action commands. The system is prepared to receive an action
    command and the devices' PTP relationships are synchronized. This allows
    actions commands to be fired across all devices, resulting in
    simultaneously acquired images with synchronized timestamps.
    Depending on the initial PTP state of each camera, it can take about
    40 seconds for all devices to autonegotiate.
"""

# Exposure time to set in microseconds
EXPOSURE_TIME_TO_SET_US = 500.0
# Delta time in nanoseconds to set action command
DELTA_TIME_NS = 1000000000

# Creating global system nodemap
sys_tl_map = system.tl_system_nodemap


def create_devices_with_tries():
    """
    This function will let users know that a device is needed and
    gives them a chance to connect a device instead of raising an exception
    """
    tries = 0
    tries_max = 6
    sleep_time_secs = 10
    while tries < tries_max:  # Wait for device for 60 seconds
        devices = system.create_device()
        if not devices:
            print(
                f'Try {tries+1} of {tries_max}: waiting for {sleep_time_secs}'
                f'secs for a device to be connected!')
            for sec_count in range(sleep_time_secs):
                time.sleep(1)
                print(f'{sec_count + 1 } seconds passed ',
                      '.' * sec_count, end='\r')
            tries += 1
        else:
            print(f'Created {len(devices)} device(s)\n')
            return devices
    else:
        raise Exception(f'No device found! Please connect a device and run '
                        f'the example again.')


def set_autonegotiation(device):
    """
    Use max supported packet size. We use transfer control to ensure that
    only one camera is transmitting at a time.
    """
    device.tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True


def set_exposure_time(device):
    """
    Manually set exposure time
    In order to get synchronized images, the exposure time must be
    synchronized as well.
    """
    dev_map = device.nodemap

    dev_map['ExposureAuto'].value = 'Off'

    Exposure_Time_node = dev_map['ExposureTime']

    min_device_exposure_time = Exposure_Time_node.min
    max_device_exposure_time = Exposure_Time_node.max

    if (EXPOSURE_TIME_TO_SET_US >= min_device_exposure_time and
            EXPOSURE_TIME_TO_SET_US <= max_device_exposure_time):
        Exposure_Time_node.value = EXPOSURE_TIME_TO_SET_US
    else:
        Exposure_Time_node.value = min_device_exposure_time


def set_trigger(device):
    """
    Enable trigger mode and set source to action
    To trigger a single image using action commands, trigger mode must
    be enabled, the source set to an action command, and the selector
    set to the start of a frame.
    """
    dev_map = device.nodemap

    dev_map['TriggerMode'].value = 'On'
    dev_map['TriggerSource'].value = 'Action0'
    dev_map['TriggerSelector'].value = 'FrameStart'


def set_action_command(device):
    """
    Prepare the device to receive an action command
    Action unconditional mode allows a camera to accept action from an
    application without write access. The device key, group key, and
    group mask must match similar settings in the system's TL node map.
    """
    dev_map = device.nodemap

    dev_map['ActionUnconditionalMode'].value = 'On'
    dev_map['ActionSelector'].value = 0
    dev_map['ActionDeviceKey'].value = 1
    dev_map['ActionGroupKey'].value = 1
    dev_map['ActionGroupMask'].value = 1


def set_transfer_control(device):
    """
    Enable user controlled transfer control
    Synchronized cameras will begin transmiting images at the same time.
    To avoid missing packets due to collisions, we will use transfer
    control to control when each camera transmits the image.
    """
    dev_map = device.nodemap

    dev_map['TransferControlMode'].value = 'UserControlled'
    dev_map['TransferOperationMode'].value = 'Continuous'
    dev_map['TransferStop'].execute()


def set_ptp(device):
    """
    Synchronize devices by enabling PTP
    Enabling PTP on multiple devices causes them to negotiate amongst
    themselves so that there is a single master device while all the
    rest become slaves. The slaves' clocks all synchronize to the
    master's clock.
    """
    device.nodemap['PtpEnable'].value = True


def set_system():
    """
    Prepare the system to broadcast an action command.
    The device key, group key, group mask, and target IP must all match
    similar settings in the devices' node maps. The target IP acts as a mask.
    """
    sys_tl_map['ActionCommandDeviceKey'].value = 1
    sys_tl_map['ActionCommandGroupKey'].value = 1
    sys_tl_map['ActionCommandGroupMask'].value = 1
    sys_tl_map['ActionCommandTargetIP'].value = 0xFFFFFFFF  # 0.0.0.0


def synchronize_cameras(devices):

    for device in devices:

        dev_map = device.nodemap
        dev_tl_map = device.tl_stream_nodemap

        # Prepare all cameras
        print(f'Setting up device {device}')

        # Set auto negotiation to true
        set_autonegotiation(device)
        print(f'Stream Auto Negotiate Packet Size Enabled :'
              f''' {dev_tl_map['StreamAutoNegotiatePacketSize'].value}''')

        # Exposure Time
        set_exposure_time(device)
        print(f'''Exposure Time : {dev_map['ExposureTime'].value}''')

        # Trigger
        set_trigger(device)
        print(f'''Trigger Source : {dev_map['TriggerSource'].value}''')

        # Action Command Preparation
        set_action_command(device)
        print('Action commands: prepared')

        # User controlled transfer control
        set_transfer_control(device)
        print('Transfer Control: prepared')

        # Prepare system
        set_system()
        print('System: prepared')

        # PTP enable
        set_ptp(device)
        print(f'''PTP Enabled : {dev_map['PtpEnable'].value}\n''')

        time.sleep(5)

    # Check for Master/Slave
    """
    Wait for devices to negotiate their PTP relationship
    Before starting any PTP-dependent actions, it is important to
    wait for the devices to complete their negotiation; otherwise,
    the devices may not yet be synced. Depending on the initial PTP
    state of each camera, it can take about 40 seconds for all devices
    to autonegotiate. Below, we wait for the PTP status of each device until
    there is only one 'Master' and the rest are all 'Slaves'.
    During the negotiation phase, multiple devices may initially come up as
    Master so we will wait until the ptp negotiation completes.
    """
    print(f'Waiting for PTP Master/Slave negotiation.'
          f'This can take up to about 40s')

    while True:
        master_found = False
        restart_sync_check = False

        for device in devices:

            ptp_status = device.nodemap['PtpStatus'].value

            # User might uncomment this line for debugging
            '''
            print(f'{device} is {ptp_status}')
            '''

            # Find master
            if ptp_status == 'Master':
                if master_found:
                    restart_sync_check = True
                    break
                master_found = True

            # Restart check until all slaves found
            elif ptp_status != 'Slave':
                restart_sync_check = True
                break

        # A single master was found and all remaining cameras are slaves
        if not restart_sync_check and master_found:
            break

        time.sleep(1)


def schedule_action_command(devices):
    """
    Set up timing and broadcast action command
    Action commands must be scheduled for a time in the future.
    This can be done by grabbing the PTP time from a device, adding
    a delta to it, and setting it as an action command's execution time.
    """
    device = devices[0]

    device.nodemap['PtpDataSetLatch'].execute()
    ptp_data_set_latch_value = device.nodemap['PtpDataSetLatchValue'].value

    print(f'\tSet action command to {DELTA_TIME_NS} nanoseconds from now')

    sys_tl_map['ActionCommandExecuteTime'].value \
        = ptp_data_set_latch_value + DELTA_TIME_NS

    print('\tFire action command')
    """
    Fire action command
    Action commands are fired and broadcast to all devices, but
    only received by the devices matching desired settings.
    """
    sys_tl_map['ActionCommandFireCommand'].execute()

    # Grab image from cameras
    for device in devices:

        # Transfer Control
        device.nodemap['TransferStart'].execute()

        buffer = device.get_buffer(timeout=2000)

        device.nodemap['TransferStop'].execute()

        print(f'\t\tReceived image from {device}'
              f' with timestamp {buffer.timestamp_ns} ns')

        device.requeue_buffer(buffer)


def example_entry_point():
    """
    // Demonstrates action commands
    // (1) manually sets exposure, trigger and action command settings
    // (2) prepares devices for action commands
    // (3) synchronizes devices and fire action command
    // (4) retrieves images with synchronized timestamps
    """

    devices = create_devices_with_tries()

    for device in devices:
        # Get device stream nodemap
        tl_stream_nodemap = device.tl_stream_nodemap

        # Enable stream auto negotiate packet size
        tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True

        # Enable stream packet resend
        tl_stream_nodemap['StreamPacketResendEnable'].value = True

    synchronize_cameras(devices)

    print('Start stream')
    for device in devices:
        device.start_stream()
    """
    Compare timestamps
    Scheduling action commands amongst PTP synchronized devices
    results synchronized images with synchronized timestamps.
    """
    schedule_action_command(devices)

    print('Stop stream and destroy all devices')
    system.destroy_device()


if __name__ == '__main__':
    print('\nWARNING:\nTHIS EXAMPLE MIGHT CHANGE THE DEVICE(S) SETTINGS!')
    print('\nExample started\n')
    example_entry_point()
    print('\nExample finished successfully')

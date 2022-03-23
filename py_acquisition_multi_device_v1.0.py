# @Author:ZhangZl
# @Date:30/11/2021

import threading

import py_acquisition_single_device as SingleDevice


def example_entry_point():

    # Create devices
    devices = SingleDevice.create_devices_with_tries()

    # Create an empty list for threads
    thread_list = []

    # Create a thread for each device
    for device in devices:
        thread = threading.Thread(target=SingleDevice.get_single_device_buffer,
                                  args=(device,))
        # Add a thread to the thread list
        thread_list.append(thread)

    # Start each thread in the thread list
    for thread in thread_list:
        thread.start()

    # Join each thread in the thread list
    """
    Calling thread is blocked util the thread object on which it was
    called is terminated.
    """
    for thread in thread_list:
        thread.join()


if __name__ == '__main__':
    print('\nAcquisition started via multi device\n')
    example_entry_point()
    print('\nAcquisition finished successfully')

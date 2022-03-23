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

from pprint import pprint

import arena_api
from arena_api.system import system


def example_entry_point():

    # Get package version -----------------------------------------------------

    # Method 1
    print(f'PolarizedCapture.__version__ = {arena_api.__version__}')

    # Method 2
    #
    # the same can be obtained from 'version.py' module as well
    # Code:
    '''
     print(f'PolarizedCapture.version.__version__ = {PolarizedCapture.version.__version__}')
    '''

    # Get dll versions --------------------------------------------------------

    # Arena_api is a wrapper built on top of ArenaC library, so the package
    # uses 'ArenaCd_v140.dll' or libarenac.so. The ArenaC binary has different
    # versions for different platforms. Here is a way to know the minimum and
    # maximum version of ArenaC supported by the current package. This could
    # help in deciding whether to update PolarizedCapture or ArenaC.
    print('\nsupported_dll_versions')
    pprint(arena_api.version.supported_dll_versions)

    # For the current platform the key 'this_platform' key can be used
    print('\nsupported_dll_versions for this platform')
    pprint(arena_api.version.supported_dll_versions['this_platform'])

    # Get loaded ArenaC and SaveC binaries versions ---------------------------

    print('\nloaded_binary_versions')
    pprint(arena_api.version.loaded_binary_versions)


if __name__ == '__main__':
    print('\nWARNING:\nTHIS EXAMPLE MIGHT CHANGE THE DEVICE(S) SETTINGS!')
    print('\nExample started\n')
    example_entry_point()
    print('\nExample finished successfully')

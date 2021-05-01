import ctypes
import os

class NoSleep:
    '''Prevent OS sleep/hibernate in windows; code from:
    https://github.com/h3llrais3r/Deluge-PreventSuspendPlus/blob/master/preventsuspendplus/core.py
    API documentation:
    https://msdn.microsoft.com/en-us/library/windows/desktop/aa373208(v=vs.85).aspx'''
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def __init__(self):
        pass


    def refresh(self):
        if os.name == 'nt':
            ctypes.windll.kernel32.SetThreadExecutionState(
                NoSleep.ES_CONTINUOUS | \
                NoSleep.ES_SYSTEM_REQUIRED)

    def __enter__(self):
        self.refresh()

    def __exit__(self, exc_type, exc_value, traceback):
        if os.name == 'nt':
            ctypes.windll.kernel32.SetThreadExecutionState(
                NoSleep.ES_CONTINUOUS)
            print("entf")

no_sleep = NoSleep()


if __name__=="__main__":
    import time
    with no_sleep:
        while True:
            time.sleep(10)
            no_sleep.refresh()

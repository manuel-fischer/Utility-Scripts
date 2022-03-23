import win32com.client
# pip install pywin32
# OR
# pip install -U pypiwin32
import time

shell = win32com.client.Dispatch("WScript.Shell")
#shell.Run("notepad")
#shell.AppActivate("Editor")
time.sleep(1)
#shell.SendKeys("Hallo Welt", 0)
#for c in "Hallo Welt":
#    shell.SendKeys(c, 0)
#    time.sleep(0.1)

# https://superuser.com/questions/329758/how-can-i-prevent-a-policy-enforced-screen-lock-in-windows
print("Toggling [NUM] to keep windows alive")
print("Press [CTRL] + [C] to close")
state = 0
try:
    while True:
        state = 1
        shell.SendKeys("{NUMLOCK}")
        time.sleep(1)
        state = 0
        shell.SendKeys("{NUMLOCK}")
        time.sleep(3)
        time.sleep(3)
        time.sleep(3)
except KeyboardInterrupt:
    if state:
        shell.SendKeys("{NUMLOCK}")

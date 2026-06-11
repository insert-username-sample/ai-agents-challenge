import subprocess
import time

print("Launching Chrome via PowerShell process...")
subprocess.Popen([
    "powershell.exe",
    "-Command",
    'Start-Process "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" -ArgumentList "--remote-debugging-port=9222", "\'--profile-directory=Profile 1\'", "\'--user-data-dir=C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data\'"'
])
time.sleep(5)

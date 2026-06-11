import subprocess
import time
import os

chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
p = subprocess.Popen([
    chrome_path,
    "--remote-debugging-port=9222",
    "--user-data-dir=C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data",
    "--profile-directory=Profile 1"
])
print("PID:", p.pid)
time.sleep(5)

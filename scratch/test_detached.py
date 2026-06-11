import subprocess
import time

chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
print("Launching detached Chrome...")
p = subprocess.Popen([
    chrome_path,
    "--remote-debugging-port=9222",
    "--user-data-dir=C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data",
    "--profile-directory=Profile 1"
], creationflags=subprocess.DETACHED_PROCESS)
print("PID:", p.pid)
time.sleep(2)

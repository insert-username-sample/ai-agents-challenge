import os
import time

chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
args = '--remote-debugging-port=9222 --profile-directory="Profile 1" --user-data-dir="C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data"'
print("Launching Chrome via os.startfile...")
os.startfile(chrome_path, arguments=args)
time.sleep(5)

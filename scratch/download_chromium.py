import os
import sys
import urllib.request
import zipfile
import shutil

def download_and_extract():
    build_url = "https://commondatastorage.googleapis.com/chromium-browser-snapshots/Win_x64/LAST_CHANGE"
    print("Fetching latest build number...")
    try:
        with urllib.request.urlopen(build_url) as response:
            build_number = response.read().decode('utf-8').strip()
    except Exception as e:
        print(f"Error fetching build number: {e}")
        return

    print(f"Latest build number is: {build_number}")
    download_url = f"https://commondatastorage.googleapis.com/chromium-browser-snapshots/Win_x64/{build_number}/chrome-win.zip"
    
    target_dir = os.path.expandvars(r"%LOCALAPPDATA%\Chromium")
    os.makedirs(target_dir, exist_ok=True)
    zip_path = os.path.join(target_dir, "chrome-win.zip")
    
    print(f"Downloading Chromium from {download_url} to {zip_path}...")
    try:
        # Simple progress report
        def report(block_num, block_size, total_size):
            read_so_far = block_num * block_size
            if total_size > 0:
                percent = read_so_far * 1e2 / total_size
                sys.stdout.write(f"\rProgress: {percent:.1f}%")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(download_url, zip_path, reporthook=report)
        print("\nDownload complete.")
    except Exception as e:
        print(f"\nError downloading Chromium: {e}")
        return

    print("Extracting Chromium...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        print("Extraction complete.")
    except Exception as e:
        print(f"Error extracting zip: {e}")
        return

    # Delete the zip file after extraction
    try:
        os.remove(zip_path)
    except Exception:
        pass

    exe_path = os.path.join(target_dir, "chrome-win", "chrome.exe")
    if os.path.exists(exe_path):
        print(f"Chromium successfully installed at: {exe_path}")
    else:
        print("Could not find chrome.exe after extraction.")

if __name__ == "__main__":
    download_and_extract()

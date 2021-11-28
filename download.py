
import os
import subprocess
from time import sleep
import pathlib

DOWNLOAD_PATH = str(pathlib.Path(__file__).parent.absolute()) + "\\output\\raw\\"

def convert():
    subprocess.Popen(["python", "-m", "http.server"])
    sleep(2)
    hashes = os.listdir(DOWNLOAD_PATH)
    for hashd in hashes:
        try:
            print(f"Downloading {hashd}.......")
            process = subprocess.Popen(["youtube-dl", "--quiet", "-i", f"http://127.0.0.1:8000/output/raw/{hashd}/master.m3u8", "-o", f"downloads/{hashd}.mp4"])
            process.wait()
            print(f"Downloaded {hashd}")
            print("--------------------------------")
        except:
            print("Error in ", hashd)
    print("Conversion Complete!")

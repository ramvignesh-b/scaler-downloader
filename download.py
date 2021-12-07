
import os
import subprocess
from time import sleep
import pathlib

DOWNLOAD_PATH = str(pathlib.Path(__file__).parent.absolute()) + "\\output\\raw\\"

def convert():
    subprocess.Popen(["python", "-m", "http.server"])
    sleep(2)
    hashes = os.listdir(DOWNLOAD_PATH)
    count = 0
    for hashd in hashes:
        print(f"Converting {hashd}.......")
        try:
            process = subprocess.Popen(["youtube-dl", "--quiet", "-i", f"http://127.0.0.1:8000/output/raw/{hashd}/master.m3u8", "-o", f"downloads/{hashd}.mp4"])
        except:
            try:
                files = os.listdir(DOWNLOAD_PATH + hashd)
                process = subprocess.Popen(["youtube-dl", "--quiet", "-i", f"http://127.0.0.1:8000/output/raw/{hashd}/{files[0]}", "-o", f"downloads/{hashd}.mp4"])
            except:
                print(f"Error while converting {hashd}")
                continue
        count = count + 1
        process.wait()
        print(f"Converting {hashd}")
        print("--------------------------------")
    print(f"Conversion Complete! Success: {count}; Failed: {len(hashes) - count}")


if __name__ == "__main__":
    convert()


import os
import pathlib

DOWNLOAD_PATH = str(pathlib.Path(__file__).parent.absolute()) + "\\output\\raw\\"
hashList = []


def rename_dir():
    dirList = os.listdir(DOWNLOAD_PATH)
    with open("output/hash.txt") as hashFile:
        hashPair = hashFile.readlines()
        for hashes in hashPair:
            pair = hashes.strip("\n").replace(':', '-').split(" || ")
            if hashList == []:
                hashList.append(pair)
            elif hashList[-1][1] == pair[1]:
                continue
            else:
                hashList.append(pair)
    for _dir in dirList:
        for _hash in hashList:
            if _dir == _hash[1]:
                try:
                    os.rename(f"{DOWNLOAD_PATH}{_dir}", f"{DOWNLOAD_PATH}{_hash[0]}")
                    print(_hash[0])
                except:
                    break
                break


if __name__ == "__main__":
    rename_dir()

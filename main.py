from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import re
from art import tprint
from time import sleep
import getpass
import shutil
import os
import pathlib
from download import convert
from rename import rename_dir


CLASSROOM = "https://www.scaler.com/academy/mentee-dashboard/classes/regular"
MASTERCLASS = "https://www.scaler.com/academy/mentee-dashboard/classes/events/masterclasses"
DOWNLOAD_PATH = str(pathlib.Path(
    __file__).parent.absolute()) + r"\output\raw\\"
DOWNLOAD_PATH = DOWNLOAD_PATH[:-1]

driver = None
videoLinks = set([])
titleSet = set([])
hashSet = set([])
name = ''


# Driver init
def init_driver():
    global driver
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory": DOWNLOAD_PATH}
    chromeOptions.add_experimental_option("prefs", prefs)
    chromeOptions.add_experimental_option(
        'excludeSwitches', ['enable-logging'])
    print("Initiating Chrome Driver...")
    driver = webdriver.Chrome(
        desired_capabilities=capabilities, options=chromeOptions)


def login():
    driver.find_element(By.NAME, 'user[email]').send_keys(EMAIL)
    driver.find_element(By.NAME, 'user[password]').send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, 'button.form__action').click()


def process_log(logs):
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if "Network.responseReceived" in log["method"]:
            yield log


def download(link, _type):
    global name
    driver.get(link)
    if _type == 'master':
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.m-header__title')))
        except TimeoutException:
            return False
        title = driver.find_element(
            By.CSS_SELECTOR, '.m-header__title')
    else:
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.event-card__content-last-button-container')))
            recordBtn = driver.find_element(
                By.CSS_SELECTOR, '.event-card__content-last-button-container')
        except TimeoutException:
            return False
        if recordBtn.text != 'Watch Recording':
            return False
        title = driver.find_element(
            By.CSS_SELECTOR, 'div.event-card__content-header')
        recordBtn.click()
    # Waiting for all the live m3u8 files to process
    sleep(7)
    events = process_log(driver.get_log("performance"))
    for event in events:
        try:
            url = event['params']['response']['url']
        except:
            continue
        if re.search('\.m3u8', url):
            flag = 0
            for item in videoLinks:
                if item == url:
                    flag = 1
                    break
            if flag:
                continue
            videoLinks.add(url)
            name = title.text
            driver.get(url)
            params = url.split('/')
            if params[2] != "www.scaler.com":
                hashd = params[7]
                hashd = hashd[:-5]
            else:
                hashd = params[4]
            titleSet.add(title)
            hashSet.add(hashd)
            with open("output/hash.txt", 'a') as output:
                output.write(f"{title.text} || {hashd}\n")
            # wait for download to complete
            sleep(3)
            dest = f"{DOWNLOAD_PATH}{hashd}"
            if not os.path.exists(dest):
                os.makedirs(dest)
            files = os.listdir(DOWNLOAD_PATH)
            for g in files:
                if g.endswith('.m3u8'):
                    try:
                        shutil.move(DOWNLOAD_PATH + g, dest)
                    except:
                        pass
                    sleep(1)
    return True


def clear_files(_file):
    with open(f"output/{_file}.txt", 'w') as output:
        output.write(f"")


def download_classroom():
    clear_files('hash')
    clear_files('failed')
    driver.get(CLASSROOM)
    login()
    success = 0
    WebDriverWait(driver, 3).until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'icon-plus-circle')))
    icons = driver.find_elements(By.CLASS_NAME, 'icon-plus-circle')
    for i in icons:
        i.click()
    elements = driver.find_elements(By.CLASS_NAME, 'me-cr-classroom-url')
    hrefs = [elem.get_attribute('href') for elem in elements]
    links = list(filter(lambda x: 'session' in x, hrefs))
    links.reverse()
    print(f"Fetched {len(links)} items from 'All Classroom'....")
    for link in links:
        ops = download(link, 'class')
        if ops:
            print(f"Successfully downloaded {name}!")
            success += 1
    print("==================================================")
    print(f"Downloaded: {success} video links")


def download_master():
    clear_files('hash')
    clear_files('failed')
    driver.get(MASTERCLASS)
    login()
    success = 0
    failed = 0
    sleep(2)
    elements = driver.find_elements(By.CLASS_NAME, 'day__link')
    links = [elem.get_attribute('href') for elem in elements]
    print(f"Fetched {len(links)} items from 'Masterclass'....")
    for link in links:
        ops = download(link, 'master')
        if ops:
            print(f"Successfully downloaded {name}!")
            success += 1
        else:
            failed += 1
            with open("output/failed.txt", 'a') as failed:
                failed.write("{link}\n")
    print("==================================================")
    print(f"Success: {success}; Failed: {failed}")


def title_hash_pair():
    with open("output/pair.txt", 'w') as pair:
        for _title, _hash in zip(titleSet, hashSet):
            pair.write(f"{_title} || {_hash}\n")


if __name__ == '__main__':
    tprint("Scaler Downloader",font="cybermedium")
    print("==================================================")
    global EMAIL, PASSWORD
    EMAIL = input("Enter email: ")
    PASSWORD = getpass.getpass("Enter password: ")
    init_driver()
    while True:
        print("What do you want me to do?")
        print("1. Download videos")
        print("2. Rename hashes")
        print("3. Convert videos")
        choice = int(input("> "))
        if choice == 1:
            print("==================================================")
            print("What do you want to download?")
            print("1. Classroom")
            print("2. Masterclass")
            print("==================================================")
            choice = int(input("> "))
            if choice == 1:
                download_classroom()
            elif choice == 2:
                download_master()
            else:
                exit(1)
            title_hash_pair()
            print("==================================================")
            choice = input("Do you want to rename and convert? y/n >")
            if choice.lower() == 'y':
                rename_dir()
                convert()
            else:
                exit(2)
        elif choice == 2:
            rename_dir()
        elif choice == 3:
            convert()
        else:
            exit(1)

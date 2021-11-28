from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import re
from time import sleep
import getpass
import shutil
import os
import pathlib
from download import convert

# Credentials
EMAIL = input("Enter email: ")
PASSWORD = getpass.getpass("Enter password: ")
DOWNLOAD_PATH = str(pathlib.Path(__file__).parent.absolute()) + r"\output\raw\\"

# Driver init
capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory": DOWNLOAD_PATH}
chromeOptions.add_experimental_option("prefs", prefs)
chromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])

DOWNLOAD_PATH = DOWNLOAD_PATH[:-1]

videoLinks = set([])
name = ''

print("Initiating Chrome Driver...")

driver = webdriver.Chrome(
    desired_capabilities=capabilities, options=chromeOptions)

driver.get("https://www.scaler.com/academy/mentee-dashboard/classes/regular")
driver.find_element(By.NAME, 'user[email]').send_keys(EMAIL)
driver.find_element(By.NAME, 'user[password]').send_keys(PASSWORD)
driver.find_element(By.CSS_SELECTOR, 'button.form__action').click()


def process_log(logs):
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if "Network.response" in log["method"]:
            yield log


def download(link):
    global name
    driver.get(link)
    sleep(2)
    try:
        recordBtn = driver.find_element(
            By.CSS_SELECTOR, '.event-card__content-last-button-container')
    except:
        return False
    if recordBtn.text != 'Watch Recording':
        return False
    title = driver.find_element(
        By.CSS_SELECTOR, 'div.event-card__content-header')
    recordBtn.click()
    sleep(3)
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
            print("-", url)
            params = url.split('/')
            if params[2] != "www.scaler.com":
                print("Host -> cloudfront")
                hashd = params[7]
                hashd = hashd[:-5]
            else:
                hashd = params[4]
            with open("output/hash.txt", 'a') as output:
                output.write(f"{title.text} || {hashd}\n")
            sleep(2)
            dest = f"{DOWNLOAD_PATH}__{hashd}"
            if not os.path.exists(dest):
                os.makedirs(dest)
            files = os.listdir(DOWNLOAD_PATH)
            for g in files:
                if g.endswith('.m3u8'):
                    try:
                        shutil.move(DOWNLOAD_PATH + g, dest)
                    except:
                        if os.path.exists(DOWNLOAD_PATH + g):
                            os.remove(DOWNLOAD_PATH + g)
                    sleep(1)
            return True
    return False


def download_source():
    success = 0
    sleep(2)
    icons = driver.find_elements(By.CLASS_NAME, 'icon-plus-circle')
    for i in icons:
        i.click()
    elements = driver.find_elements(By.CLASS_NAME, 'me-cr-classroom-url')
    links = [elem.get_attribute('href') for elem in elements]
    links.reverse()
    print("Fetched items from 'All Classroom'....")
    for link in links:
        ops = download(link)
        if ops:
            print(f"Successfully downloaded {name}!")
            success += 1
    print("=========================")
    print("Done: ", success, " video links")

hashList = set([])

def check_hash(title):
    flag = 0
    for _hash in hashList:
        if title == _hash:
            flag = 1
            break
    if flag:
        return False
    return True


if __name__ == '__main__':
    print("=========================")
    download_source()
    convert()

import csv
import os
import json
import time
import random
from os import system, name
from datetime import datetime
import undetected_chromedriver as uc
from typing import Dict, List
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCRAPPER = False

start_time = time.time()

def driverInit():
    option = uc.ChromeOptions()
    useragentstr = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"
    option.add_argument("--log-level=3")
    option.add_argument("--disable-infobars")
    option.add_argument("--disable-extensions")
    option.add_argument("--headless")
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False,
             "profile.default_content_setting_values.notifications": 2
             }
    option.add_experimental_option("prefs", prefs)

    option.add_argument(f"user-agent={useragentstr}")
    driverr = uc.Chrome(options=option)
    return driverr


def scroll_down(driver):
    SCROLL_PAUSE_TIME = 1
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        time.sleep(2)

def domain_to_url(domain: str) -> str:
    if domain.startswith(".") and "www" not in domain:
        domain = "www" + domain
        return "https://" + domain
    elif "www" in domain and domain.startswith("."):
        domain = domain[1:]
        return "https://" + domain
    else:
        return "https://" + domain


def login_using_cookie_file(driver: WebDriver, cookie_file: str):
    """Restore auth cookies from a file. Does not guarantee that the user is logged in afterwards.
    Visits the domains specified in the cookies to set them, the previous page is not restored."""
    domain_cookies: Dict[str, List[object]] = {}
    with open(cookie_file) as file:
        cookies: List = json.load(file)
        # Sort cookies by domain, because we need to visit to domain to add cookies
        for cookie in cookies:
            try:
                domain_cookies[cookie["domain"]].append(cookie)
            except KeyError:
                domain_cookies[cookie["domain"]] = [cookie]

    for domain, cookies in domain_cookies.items():
        driver.get(domain_to_url(domain + "/robots.txt"))
        for cookie in cookies:
            cookie.pop("sameSite", None)  # Attribute should be available in Selenium >4
            cookie.pop("storeId", None)  # Firefox container attribute
            try:
                driver.add_cookie(cookie)
            except:
                print(f"Couldn't set cookie {cookie['name']} for {domain}")
    return True

def returnFiletoList(filename):
    with open(filename, "r") as f:
        LinesToList = f.read().split("\n")
    return LinesToList


def run():
    global driver
    print("Connecting.")
    TKScrollTXT1 = "Hi! [name] What you doing these days"
    driver = driverInit()
    driver.get("https://www.linkedin.com")
    time.sleep(5)
    driver.find_element(By.XPATH, "/html/body/main/section[1]/div/div/form/div[2]/div[1]/input").send_keys("exploretheweb@yahoo.com")
    time.sleep(1.5)
    driver.find_element(By.XPATH, "/html/body/main/section[1]/div/div/form/div[2]/div[2]/input").send_keys("123PPH123*")
    driver.find_element(By.XPATH, "/html/body/main/section[1]/div/div/form/button").click()
    time.sleep(5)
    all_keywords=returnFiletoList("keywords.txt")
    csvfile=open("database.csv",'a')
    csvwrite=csv.writer(csvfile)
    for key in all_keywords:
        if time.time() - start_time > 1800:
            break
        driver.get(f"https://www.linkedin.com/search/results/all/?keywords={key.replace(' ','%20')}&origin=GLOBAL_SEARCH_HEADER&sid=.Bm")
        time.sleep(5)
        driver.find_element(By.XPATH, "/html/body/div[4]/div[3]/div[2]/section/div/nav/div/ul/li[1]/button").click()
        time.sleep(4)


        finalUrl = driver.current_url
        if "results" and "people" not in finalUrl:
            print("Incorrect Url", "The page you open is does not contain any profile links")
            driver.quit()
            return
        counter = 1
        while True:
            try:
                driver.get(f"{finalUrl}&page={counter}")
                time.sleep(3)
                scroll_down(driver)
                time.sleep(2)
                pChk = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, "//span[@class='entity-result__title-line entity-result__title-line--2-lines']//a")))
                if pChk:
                    allUrls = driver.find_elements(by=By.XPATH,
                                                   value="//ul[@class='reusable-search__entity-result-list list-style-none']//span[@class='entity-result__title-line entity-result__title-line--2-lines']//a//span//span[1]")
                    for a in allUrls:
                        if time.time()-start_time > 1800:
                            break
                        try:
                            print(a.text)
                            connectBtn = driver.find_element(By.XPATH,
                                                             f"//button[@aria-label='Invite {str(a.text).strip()} to connect']")
                            actions = ActionChains(driver)
                            actions.move_to_element(connectBtn).perform()
                            time.sleep(0.5)
                            connectBtn.click()
                            try:
                                addNoteBtn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                                    (By.XPATH, "(//span[@class='artdeco-button__text' and text()='Add a note'])")))
                                addNoteBtn.click()
                                msgSend = str(TKScrollTXT1)
                                msgSend = msgSend.replace("[name]", f"{str(a.text).strip()}")
                                writeMsgArea = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                                    (By.XPATH, "//textarea[contains(@class,'ember-text-area ember-view')]")))
                                writeMsgArea.send_keys(msgSend)
                                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                            "(//button[contains(@class,'artdeco-button artdeco-button--2') and @aria-label='Send now'])"))).click()
                                insertText = f"\n[Info] Connect Sent to : {a.text}"
                                print(insertText)
                                print(time.time() - start_time)
                            except:
                                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                            "(//button[contains(@class,'artdeco-button artdeco-button--2') and @aria-label='Send now'])"))).click()
                            t_delay = random.randint(40, 70)
                            print(f"\n[Info] Sleeping for {t_delay} secs")
                            time.sleep(t_delay)
                            csvwrite.writerow([a,key,datetime.now()])
                            csvfile.flush()
                        except:
                            pass
                            #print(f"\n[Info] No Connect Button Found for : {a.text}")
                counter += 1
            except:
                print("\n[Info] No more profiles found....")
                driver.quit()
                break
    driver.quit()
    startBot1.config(state="active")



def updator():
    try:
        system('taskkill /F /IM chromedriver.exe /T')
        os.remove(f"{os.getcwd()}/chromedriver.exe")
    except:
        pass



run()

from pymongo import MongoClient
import csv
import logging
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
import logging
from datetime import datetime


SCRAPPER = False


class Solution:
    def solve(self, s0, s1):
        s0 = s0.lower()
        s1 = s1.lower()
        s0List = s0.split(" ")
        s1List = s1.split(" ")
        return len(list(set(s0List) & set(s1List)))


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
    cluster = MongoClient("mongodb+srv://user1:yes321@cluster0.m6tusxx.mongodb.net/?retryWrites=true&w=majority")
    db = cluster["linkedin"]
    collection = db["login"]
    initial_data = list(collection.find())
    collection1 = db["connections"]
    collection2 = db["excel_data"]
    initial_con = list(collection1.find())
    n = len(initial_data)
    print(initial_data[n - 1])

    cn = len(initial_con)
    d_n = len(list(collection2.find()))
    basic_data = list(collection2.find())[d_n-1]


    acc_conf = []
    sent_conf = []
    prev_conf = []
    name = basic_data['Name']
    ability = basic_data['Ability']
    sent_time = basic_data['Time']
    sent_status = basic_data['Sent-Status']
    location = basic_data['Location']
    c_name = basic_data['Company']
    c_designation = basic_data['Designation']

    TKScrollTXT1 = "Hi [name] I hope this message finds you well. My name is [Your Name] and I specialize in AI and automation for [keyword] agencies. I recently came across your ability, and was impressed with the work you've done in the [keyword] field. As the founder of a [keyword] agency, I'm sure you're always looking for ways to improve efficiency and stay ahead of the curve. I believe that AI and automation can play a significant role in helping [keyword] agencies achieve these goals. As someone who has experience in this area, I'd love to connect and see if there might be opportunities to collaborate or exchange ideas. Best Regards [Your Name]"
    TKScrollTXT2 = "Hi [name], I hope this message finds you well. My name is [Your Name] and I specialize in AI and automation for [keyword] agencies. I recently came across your ability, and was impressed with the work you do in the [keyword] field. As the manager of a [keyword] agency, I'm sure you're always looking for ways to improve efficiency and stay ahead of the curve. I believe that AI and automation can play a significant role in helping [keyword] agencies achieve these goals. As someone who has experience in this area, I'd love to connect and see if there might be opportunities to collaborate or exchange ideas. Would you be open to discussing how AI and automation could potentially benefit your business? I'd love to schedule a call at your convenience to learn more about your needs and see if my expertise might be able to assist in any way. Thank you for considering my request. I look forward to connecting with you. Best regards, [Your Name]"
    TKScrollTXT3 = "Hello [name], I hope this message finds you well. My name is [Your Name] and I specialize in helping businesses, like yours, save time and streamline their processes through the use of AI and automation. As someone who works in [keyword], I'm sure you understand the importance of staying up-to-date with the latest trends and technologies in order to achieve your business goals. However, with so many tasks and responsibilities on your plate, it can be difficult to find the time to do everything that needs to be done. That's where AI and automation come in. By using these tools, you can automate repetitive and time-consuming tasks, freeing up your time to focus on more important, high-value work. I believe that our AI and automation solutions could be a valuable asset to your business. Would you be open to discussing how these tools could potentially benefit your ability and save you time? I'd love to schedule a call at your convenience to learn more about your needs and see if our solutions might be a good fit. Thank you for considering my request. I look forward to connecting with you. Best regards, [Your Name]"

    for c in range(0, len(initial_data[n - 1]['cookies'])):
        cus_name = name[c]
        cus_ability = ability[c]
        cus_sent_time = sent_time[c]
        cus_sent_status = sent_status[c]
        location_in = location[c]
        cus_company_name = c_name[c]
        cus_company_designation = c_designation[c]
        keyword = initial_data[n - 1]['keyword'][c]
        start_time = time.time()
        cookies = initial_data[n - 1]['cookies'][c]
        print(cookies)
        connect = int(initial_con[cn - 1]['sent_con'][c])

        file = open("initial.txt", "w")
        file.write(cookies.decode('utf-8'))
        file.close()

        global driver
        ob = Solution()
        director = "Director CEO Founder"
        manager = "Manager Head"
        print("Connecting.")
        driver = driverInit()
        login_using_cookie_file(driver, "initial.txt")
        driver.get("https://www.linkedin.com")
        time.sleep(7)

        #my_name = ((driver.find_element(By.XPATH,
         #                               "/html/body/div[5]/div[3]/div/div/div[2]/div/div/div/div[1]/div[1]/a[1]/div[2]").text).split(
          #  ","))[1]

        #print(my_name)
        try:
            driver.get("https://www.linkedin.com/mynetwork/")
            time.sleep(7)
            t = driver.find_element(By.CLASS_NAME, "pl3").text
            t = t.replace(",", "")
            if initial_con[cn - 1]['prev_con'][c] == 0:
                accepted_co = 0
            else:
                accepted_co = int(t) - int(initial_con[cn - 1]['prev_con'][c])
            previous_co = int(t)

            acc_conf.append(accepted_co)
            prev_conf.append(previous_co)
        except:
            acc_conf.append(0)
            prev_conf.append(0)

        print("Accepted Connects: ", accepted_co)

        all_keywords = [initial_data[n - 1]['keyword'][c]]
        csvfile = open("database.csv", 'a')
        csvwrite = csv.writer(csvfile)

        for key in all_keywords:
            if time.time() - start_time > 600:
                break
            driver.get(
                f"https://www.linkedin.com/search/results/people/?keywords={key.replace(' ', '%20')}&origin=GLOBAL_SEARCH_HEADER&sid=Bp%3B")
            time.sleep(5)

            finalUrl = driver.current_url
            if "results" and "people" not in finalUrl:
                print("Incorrect Url", "The page you open is does not contain any profile links")
                driver.quit()
                return
            counter = 1
            while True:
                try:
                    if time.time() - start_time > 600:
                        break
                    in_count = 1
                    driver.get(f"{finalUrl}&page={counter}")
                    time.sleep(3)
                    scroll_down(driver)
                    time.sleep(2)
                    # pChk = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    #   (By.XPATH, "//span[@class='entity-result__title-line entity-result__title-line--2-lines']//a")))
                    # if pChk:
                    # allUrls = driver.find_elements(by=By.XPATH,
                    # value="//ul[@class='reusable-search__entity-result-list list-style-none']//span[@class='entity-result__title-line entity-result__title-line--2-lines']//a//span//span[1]")
                    allUrls = []
                    # time.sleep(100)
                    for u in range(1, 11):
                        try:
                            allUrls.append(driver.find_element(By.XPATH,
                                                               '/html/body/div[4]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[' + str(
                                                                   u) + ']/div/div/div[2]/div[1]/div[1]/div/span[1]/span/a/span/span[1]'))
                        except:
                            try:
                                allUrls.append(driver.find_element(By.XPATH,
                                                                   '/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[' + str(
                                                                       u) + ']/div/div/div[2]/div[1]/div[1]/div/span[1]/span/a/span/span[1]'))
                            except:
                                try:
                                    allUrls.append(driver.find_element(By.XPATH,
                                                                       '/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[3]/div/ul/li[' + str(
                                                                           u) + ']/div/div/div[2]/div[1]/div[1]/div/span[1]/span/a/span/span[1]'))
                                except:
                                    allUrls.append(driver.find_element(By.XPATH,
                                                                       '/html/body/div[4]/div[3]/div[2]/div/div[1]/main/div/div/div[3]/div/ul/li[' + str(
                                                                           u) + ']/div/div/div[2]/div[1]/div[1]/div/span[1]/span/a/span/span[1]'))

                    for a in allUrls:
                        if time.time() - start_time > 600:
                            break
                        try:
                            # a.click()
                            #time.sleep(100)
                            print(a.text)

                            destn = driver.find_element(By.XPATH,
                                                        "(//div[contains(@class,'entity-result__primary-subtitle t-14')])[" + str(
                                                            in_count) + "]").text
                            # loc = driver.find_element(By.XPATH,
                            #                         "(//div[contains(@class,'linked-area flex-1')]//div)[" + str(
                            #                            in_count + 1) + "]").text
                            try:
                                loc = driver.find_element(By.XPATH,
                                                          '/html/body/div[4]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[' + str(
                                                              in_count) + ']/div/div/div[2]/div[1]/div[2]/div[2]').text
                            except:
                                try:
                                    loc = driver.find_element(By.XPATH,
                                                              '/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[' + str(
                                                                  in_count) + ']/div/div/div[2]/div[1]/div[2]/div[2]').text
                                except:
                                    try:
                                        loc = driver.find_element(By.XPATH,
                                                                  '/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[3]/div/ul/li[' + str(
                                                                      in_count) + ']/div/div/div[2]/div[1]/div[2]/div[2]').text
                                    except:
                                        try:
                                            loc = driver.find_element(By.XPATH,
                                                                  '/html/body/div[4]/div[3]/div[2]/div/div[1]/main/div/div/div[3]/div/ul/li[' + str(
                                                                      in_count) + ']/div/div/div[2]/div[1]/div[2]/div[2]').text
                                        except:
                                            loc = "Not provided"
                            try:
                                c_details = driver.find_element(By.XPATH,
                                                          '/html/body/div[4]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[' + str(
                                                              in_count) + ']/div/div/div[2]/div[2]/p').text
                                try:
                                    split_fun = c_details.split(" at")
                                    company_designation = split_fun[0]
                                    company_name = split_fun[1]
                                except:
                                    c_details = "Not Provided"
                                    company_name = c_details
                                    company_designation = c_details
                            except:
                                try:
                                    c_details = driver.find_element(By.XPATH,
                                                              '/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[' + str(
                                                                  in_count) + ']/div/div/div[2]/div[2]/p').text
                                    try:
                                        split_fun = c_details.split(" at")
                                        company_designation = split_fun[0]
                                        company_name = split_fun[1]
                                    except:
                                        c_details = "Not Provided"
                                        company_name = c_details
                                        company_designation = c_details
                                except:
                                    try:
                                        c_details = driver.find_element(By.XPATH,
                                                                  '/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[3]/div/ul/li[' + str(
                                                                      in_count) + ']/div/div/div[2]/div[2]/p').text
                                        try:
                                            split_fun = c_details.split(" at")
                                            company_designation = split_fun[0]
                                            company_name = split_fun[1]
                                        except:
                                            c_details = "Not Provided"
                                            company_name = c_details
                                            company_designation = c_details
                                    except:
                                        try:
                                            c_details = driver.find_element(By.XPATH,
                                                                  '/html/body/div[4]/div[3]/div[2]/div/div[1]/main/div/div/div[3]/div/ul/li[' + str(
                                                                      in_count) + ']/div/div/div[2]/div[2]/p').text
                                            try:
                                                split_fun = c_details.split(" at")
                                                company_designation = split_fun[0]
                                                company_name = split_fun[1]
                                            except:
                                                c_details = "Not Provided"
                                                company_name = c_details
                                                company_designation = c_details


                                        except:
                                            c_details = "Not Provided"
                                            company_name = c_details
                                            company_designation = c_details



                            print(destn)
                            print(loc)
                            print(company_name)
                            print(company_designation)

                            in_count = in_count + 1

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
                                if ob.solve(destn, manager) == 1:
                                    msgSend = str(TKScrollTXT2)
                                    msgSend = msgSend.replace("[name]", f"{str(a.text).strip()}")
                                    msgSend = msgSend.replace("[Your Name]", my_name.strip())
                                    msgSend = msgSend.replace("[keyword]", keyword)


                                    writeMsgArea = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                                        (By.XPATH, "//textarea[contains(@class,'ember-text-area ember-view')]")))
                                    writeMsgArea.send_keys(msgSend)
                                elif ob.solve(destn, director) == 1:
                                    msgSend = str(TKScrollTXT3)
                                    msgSend = msgSend.replace("[name]", f"{str(a.text).strip()}")
                                    msgSend = msgSend.replace("[Your Name]", my_name.strip())
                                    msgSend = msgSend.replace("[keyword]", keyword)

                                    writeMsgArea = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                                        (By.XPATH, "//textarea[contains(@class,'ember-text-area ember-view')]")))
                                    writeMsgArea.send_keys(msgSend)
                                else:
                                    msgSend = str(TKScrollTXT1)
                                    msgSend = msgSend.replace("[name]", f"{str(a.text).strip()}")
                                    msgSend = msgSend.replace("[Your Name]", my_name.strip())
                                    msgSend = msgSend.replace("[keyword]", keyword)

                                    writeMsgArea = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                                        (By.XPATH, "//textarea[contains(@class,'ember-text-area ember-view')]")))
                                    writeMsgArea.send_keys(msgSend)

                                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                            "(//button[contains(@class,'artdeco-button artdeco-button--2') and @aria-label='Send now'])"))).click()
                                insertText = f"\n[Info] Connect Sent to : {a.text}"
                                connect = connect + 1
                                print(insertText)
                                print(time.time() - start_time)
                            except:
                                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                            "(//button[contains(@class,'artdeco-button artdeco-button--2') and @aria-label='Send now'])"))).click()
                            t_delay = random.randint(40, 70)
                            cus_sent_time.append(datetime.now())
                            cus_ability.append(destn)
                            cus_name.append(a.text)
                            cus_sent_status.append("Request Sent")
                            cus_company_name.append(company_name)
                            cus_company_designation.append(company_designation)
                            location_in.append(loc)
                            print(f"\n[Info] Sleeping for {t_delay} secs")

                            time.sleep(t_delay)
                            csvwrite.writerow([a.text, key, datetime.now()])
                            csvfile.flush()
                        except:
                            # logging.exception('msg')

                            pass
                            # print(f"\n[Info] No Connect Button Found for : {a.text}")
                    counter += 1
                except:
                    print("\n[Info] No more profiles found....")
                    driver.quit()
                    break
        sent_conf.append(connect)
        name.append(cus_name)
        ability.append(cus_ability)
        sent_status.append(cus_sent_status)
        sent_time.append(cus_sent_time)
        location.append(location_in)
        c_name.append(cus_company_name)
        c_designation.append(cus_company_designation)
        driver.quit()
    collection1.insert_one({'prev_con': prev_conf, 'acc_con': acc_conf, 'sent_con': sent_conf})
    collection2.insert_one(
        {'Name': name, 'Designation': c_designation, 'Company': c_name, 'Ability': ability, 'Time': sent_time, 'Sent-Status': sent_status, 'Location': location})


def updator():
    try:
        system('taskkill /F /IM chromedriver.exe /T')
        os.remove(f"{os.getcwd()}/chromedriver.exe")
    except:
        pass


run()

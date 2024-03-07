'''
Extracts company top people from given list of companies.

Requirements:
1. company.csv file with minimum CSV Schema -> (company_name,website)
2. Need to have apollo logged in , in chrome.
3. Provide profile path in `user_data_dir`
'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
import csv
import pandas as pd
from tqdm import tqdm
import pickle


# --------------- Configurations ------------------
user_data_dir = "C:/Users/<Your_Windows_User_name>/AppData/Local/Google/Chrome/User Data" #Replace with your chrome profile
people_filter_link = """
    https://app.apollo.io/#/people?finderViewId=5a205be49a57e40c095e1d60&page=1&personTitles[]=ceo&personTitles[]=CTO&personTitles[]=CFO&personTitles[]=COO&personTitles[]=Co-founder&personTitles[]=Founder&personTitles[]=MD&personTitles[]=Technical%20Lead&personTitles[]=Engineering%20Manager&personTitles[]=IT%20manager
 """ # Replace with another apollo /people filter link for another set of filters

save_file = "company_people_data.csv" #provide file name for saving final data

options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={user_data_dir}")
options.add_argument("profile-directory=Default")

#This will store final data
company_data_with_people = [["company_name", "website","designation", "email", "name" "linkedin" ]] #Add other fields as in company.csv

df = pd.read_csv("company.csv")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()) , options=options)

first = True
scrapped_now = 0
MAX_ALLOWED_SCRAP = 5000 #Limit max scraps to 5000
for index,company in df.iterrows():
    all = []
    try:
        page = driver.get(people_filter_link)
        # ToDo: Extract designation , phone number , email , linkendin
        time.sleep(4)
        # REGION----- Send company link in filter and search
        filters = driver.find_elements(By.CLASS_NAME , 'zp_TMbya')
        if first:
            filters[4].click()
            first = False
        else:
            filters[4].click()
            time.sleep(0.5)
            filters[4].click()
        time.sleep(1)
        search_box = driver.find_element(By.CLASS_NAME , 'Select-input')
        search_box.send_keys(company["company_name"]) #send company link in filter to search
        time.sleep(1)
        search_box.send_keys(Keys.ENTER)  
        time.sleep(1)
        search_box.send_keys(Keys.ENTER) 
        time.sleep(2)
        # ENDREGION -----------
    
        people_box = driver.find_elements(By.CLASS_NAME , 'zp_RFed0') 
        for person in people_box[:6]:
                if scrapped_now >= MAX_ALLOWED_SCRAP:
                    break
                skip_email = False
                try:
                    linked_in = str()
                    apollo_link = str()
                    links = person.find_elements(By.TAG_NAME , 'a') #all the links for that person
                    for i in links:
                        try:
                            link = i.get_attribute('href')
                            if r'www.linkedin.com/in' in link:
                                linked_in = link
                                print(link)
                        except:
                            continue

                    job_position = person.find_element(By.CLASS_NAME , 'zp_Y6y8d')
                    person_job_position = job_position.text
                    name = person.find_element(By.CLASS_NAME , 'zp_xVJ20')
                    person_name = name.text
                    print(person_name)
                    print(person_job_position)
                    try:
                        email_access = person.find_element(By.CLASS_NAME , 'zp_n9QPr')
                        email_access.click()
                        scrapped_now +=1
                    except:
                        try:
                            email_access = person.find_element(By.CLASS_NAME , 'zp_IYteB')
                            email_access.click()
                            scrapped_now +=1
                        except:
                            print("Exception: email SKIPPING inner")
                            skip_email = True
                            pass
                            
                    time.sleep(1)
                    if skip_email:
                        email = ''
                        all.append(
                        [   #Add all the fields needed from company.csv
                            company["company_name"],
                            company["website"],
                            person_job_position ,
                            "",
                            person_name  ,
                            linked_in
                        ]
                        )
                    else:
                        time.sleep(4)
                        try:
                            email = driver.find_element(By.CLASS_NAME, "zp_t08Bv")
                            person_email = email.text
                            print(person_email)
                            print("--------------")
                            all.append(
                                [   #Add all the fields needed from company.csv
                                    company["company_name"],
                                    company["website"],
                                    person_job_position ,
                                    person_email ,
                                    person_name ,
                                    linked_in
                                ]
                                )
                            
                            print(person_email)
                        except:
                             all.append(
                            [   
                                #Add all the fields needed from company.csv
                                company["company_name"],
                                company["website"],
                                person_job_position ,
                                "",
                                person_name  ,
                                linked_in
                            ]
                            )
                    time.sleep(3)
                    try:
                        random_btn = driver.find_element(By.CLASS_NAME , 'add-contact-account-dropdown')
                        random_btn.click()
                        time.sleep(1)
                        random_btn.click()
                        time.sleep(1)
                    except:
                        pass
                except Exception as e:
                    print(f"Exception: SKIPPING -- {e}")
        
    except:
        print(f"Skipping {company["company_name"]}")

    with open(save_file, 'a', newline='', encoding='utf-8') as fp:
        writer = csv.writer(fp)
        writer.writerows(all)
    print(f"Done till id = {index} , {company[0]}")
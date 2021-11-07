# %%
import pandas as pd
import openpyxl as pxl

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as e

import time
import re
import traceback
# %%
def call_driver_and_get(url):
    
    """
    This function instantiates a remotely operated browser and go the url page.

    Returns:
        [WebDriver]: A driver.
    """
    
    try:
    
        DRIVER_REL_PATH = r'parent_directory\scraper\driver\chromedriver.exe'

        driver = webdriver.Chrome(DRIVER_REL_PATH)
        
        driver.get(url)
        driver.maximize_window()
        
    except:
        print(e)
        traceback.print_exc()

    return driver 
# %%

# click load button until finish
def load_button(driver):
    
    """
    This function clicks load button until the last load.
    """
    
    LOAD_MORE_XPATH = '//*[@id="react-app"]/div/div/div/div[2]/div/div[2]/div/div[2]/div[2]/button'

    while True:
        
        try:
            
            load_more = driver.find_element_by_xpath(LOAD_MORE_XPATH)
            time.sleep(3)
            load_more.click()
            time.sleep(3)
            
        except Exception as e:
            print (e)
            break
        
    # %%
    
def club_pages():
    
    """
    Enters in every club's link and gets the clubs name and email (if there is any specified in the `E: `)

    Returns:
        [string]: two lists of strings. First with the club names, and second with the respective email or 'empty'     if there is any.
    """
    # xpath to club, club name and email
    CLUB_XPATH = '//*[@id="org-search-results"]/div/div/div'
    EMAIL_XPATH = '//*[@id="react-app"]/div/div/div/div/div[1]/div[1]/div/div[3]/div/div[2]/div[2]'
    CLUB_NAME_XPATH = '//*[@id="react-app"]/div/div/div/div/div[1]/div[1]/div/div[1]/h1'

    # club name and email list
    club_name = []
    club_email = []   

    # counter
    i = 1
    while True:
        try:
            club_page = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, CLUB_XPATH + '[' + str(i) + ']'))
    )
            club_page.click()
            try:
                name = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, CLUB_NAME_XPATH))
                )
                club_name.append(name.text)

                try:
                    email = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, EMAIL_XPATH))
                    )
                    club_email.append(email.text)

                except:
                    email = 'empty'
                    club_email.append(email)
                    
            except:
                driver.get(CLUB_XPATH + '[' + str(i) + ']')
            
            i += 1      
            driver.back()

        except:

            return club_name, club_email
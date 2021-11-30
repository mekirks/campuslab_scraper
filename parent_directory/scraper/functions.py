# %%
from sre_constants import error
import pandas as pd
import openpyxl as pxl

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common import exceptions as e

import time
import datetime
import re
import traceback


#! EXTRACTION

def call_driver_(url):
    
    """
    This function instantiates a remotely operated browser.

    Returns:
        [WebDriver]: A driver.
    """
    DRIVER_PATH = r'/Users/studocu/Downloads/campuslab_scraper-main/parent_directory/scraper/driver/chromedriver.exe'    
    driver = webdriver.Chrome(DRIVER_PATH)
    
    driver.get(url)
    driver.maximize_window()

    return driver 


def load_button_(driver):
    
    """
    This function clicks load button until the last load.
    """
    
    LOAD_MORE_XPATH = r'//span[text()="Load More"]'
    
    while True:
        
        try:
            
            load_more = driver.find_element_by_xpath(LOAD_MORE_XPATH)

            actions = ActionChains(driver)
            actions.move_to_element(load_more).perform()

            driver.execute_script('arguments[0].scrollIntoView({behavior: "smooth", block: "center", inline: "center"});', load_more)
           
            WebDriverWait(driver, 4).until(
        EC.element_to_be_clickable((By.XPATH, LOAD_MORE_XPATH)))
            
            load_more.click()
            
        except:
            
            break
        
        
def get_links_(driver):
    
    LINKS_PATH = r'//ul[@class="MuiList-root MuiList-padding"]//a'
    
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,LINKS_PATH)))    
    
    links_web_elem = driver.find_elements_by_xpath(LINKS_PATH)
    
    links = []
    for link in links_web_elem:
        
        links.append(link.get_attribute('href'))
        
    return links


def pull_association_info_(links, driver):
        
    all_rows = []
    error_links = []
      
    for i, link in enumerate(links):
    
        driver.get(link)
        
        
        try:
        
            NAME_XPATH = r'//h1'
            DESC_XPATH = r'//div[@class="bodyText-large userSupplied"]'
            ADDRESS_XPATH = r'//span[text()="Address"]/..'
            EMAIL_XPATH = r'//span[text()="Contact Email"]/..'
            PHONE_XPATH = r'//span[text()="Phone Number"]/..'
            XPATH_LINK = r''

            INFO_XPATHS = [NAME_XPATH, DESC_XPATH, ADDRESS_XPATH, EMAIL_XPATH, PHONE_XPATH, XPATH_LINK]
            INFO_NAMES = ['ASSOCIATION NAME','ASSOCIATION DESCRIPTION', 'ASSOCIATION ADDRESS', 'ASSOCIATION EMAIL', 'ASSOCIATION PHONE', 'ASSOCIATION LINK']

            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, INFO_XPATHS[0])))

            all_info_row = []
            
            print('PULLING DATA FROM ASSOCIATION ' + str(i) + ' OUT OF ' + str(len(links)) + ' ASSOCIATIONS...')
            
            for info_name, info_xpath in zip(INFO_NAMES, INFO_XPATHS):

                try:
                            
                    if info_xpath != '':
                        
                        info_data_web_elem = driver.find_element_by_xpath(info_xpath)
                        info_data = info_data_web_elem.text
                        
                        if info_name == 'ASSOCIATION NAME':
                            info_data = info_data_web_elem.text.title()                           
                            
                        
                        # treating if description is empty 
                        if info_data == '':
                            
                            all_info_row.append('Null')        
                        
                        # treating if address is empty
                        elif info_data == 'Address':
                            
                            all_info_row.append('Null')
                            
                        # treating if email is empty    
                        elif info_data == 'Contact Email\nE: ':
                            
                            all_info_row.append('Null')
                            
                        # cleaning email data
                        elif info_data.startswith('Contact Email'):
                            
                            info_data = re.sub('Contact Email\nE: ', '', info_data)
                            all_info_row.append(info_data.lower())
                            
                        # cleaning phone data
                        elif info_data.startswith('Phone'):
                            
                            info_data = re.sub('Phone Number\nP: ', '', info_data)
                            all_info_row.append(info_data)
                        else:
                            
                            all_info_row.append(info_data)
                            
                    else:
                        
                        all_info_row.append(link)

                except:
                    
                    all_info_row.append('Null')
            
        except:
            
            print(e)
            traceback.print_exc()
            error_links.append(link)
            pass
        
        all_rows.append(all_info_row)
        
    return all_rows, error_links
    
    


def extract_(url):
    
    
    print('CALLING DRIVER...')
    driver = call_driver_(url)
    print('DRIVER CALLED.')
    
    
    print('LOADIND BUTTONS...')
    load_button_(driver)
    print('ALL BUTTONS LOADED.')
    
    
    
    print('PULLING LINKS...')
    links = get_links_(driver)
    print('LINKS PULLED.')
    
    print('PULLING ASSOCIATION DATA...')
    all_rows, error_links = pull_association_info_(links, driver)
    print('ASSOCIATION DATA PULLED')
    
    print('CLOSING DRIVER...')
    driver.close()
    print('DRIVER CLOSED.')
    
    if len(error_links)==0:
        
        return all_rows
    
    else:
        
        if((len(error_links)))>1: 
            
            print(str(len(error_links)) + ' association sites failed.\n')
            
            for link in error_links:
                print(link)

        elif((len(error_links)))==1:
            
            print('One association link failed: ' + error_links)
            
        #! here we could call the function again on the error_links
        
        elif ((len(error_links)))==0:
            
            print('All associations was scraped.')
            
    return all_rows


# ! WRANGLING 

def transform_(all_rows):
    
    try:       
        
        df = pd.DataFrame(all_rows, columns=['Name', 'Descrip', 'Address', 'Email', 'Phone', 'Link'])
        df = df[['Name', 'Email']]
        df = df.loc[(df['Name'] != 'Null') & (df['Email'] != 'Null')]
        print(df)
        
    except:
        
        print(e)
        traceback.print_exc()
        pass
      
    return df  
    


def load_(file_name, df):
    
    """
    This function gets a file name and a DataFrame and converts into a excel file, and save it at excel_files folder.

    Args:
        file_name (str): the excel file name that it will be created, WITHOUT the extension.
        df (pd.DataFrame): a DataFrame containing the code (if any) and courses name.
    """

    EXCEL_FILES_PATH = r'C:/Users/studocu/Downloads'
    EXTENSION = '.xlsx'
    PATH_FILE = EXCEL_FILES_PATH + '/' + file_name + EXTENSION
    df.to_excel(PATH_FILE, index=False, engine='xlsxwriter')




def pipeline(url, uniID, uni_name):
    
    
    file_name = uniID + ' ' + uni_name + ' ASSOCIATIONS'
    file_name = re.sub(' ', '_', file_name)
    all_rows = extract_(url)
    
    df_ = transform_(all_rows)
    

    
    load_(file_name, df_)
    

def scrape_single(url, uniID, uni_name):
    
    pipeline(url, uniID, uni_name)
    

def scrape_multiples():
    
    start_time = time.time()
    
    EXCEL_PATH = r'/Users/studocu/Library/Containers/com.microsoft.Excel/Data/Downloads/input.xlsx'

    df_ = pd.read_excel(EXCEL_PATH)

    urls = df_.iloc[:,0]
    uni_IDS = df_.iloc[:,1]
    uni_names = df_.iloc[:,2]
    
    for i, url in enumerate(urls):
        
        uni_ID = str(uni_IDS[i])
        uni_name = uni_names[i]
        
        print('PULLING DATA FROM: ' + uni_name)
        pipeline(url,uni_ID, uni_name)
        
    
    
    total_seconds = time.time() - start_time
    
    if total_seconds <= 60:
        
        print("EXECUTION TIME: {:.2f} SECONDS".format(total_seconds))
    
    else:
        
        print("EXECUTION TIME: {} ".format(datetime.timedelta(seconds=total_seconds)))
        
# %%
# %%

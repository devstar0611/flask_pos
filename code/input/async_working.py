from selenium import webdriver
from getpass import getpass
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
from bs4 import BeautifulSoup
from icecream import ic
import pandas as pd
import datetime
import requests
import argparse
import sys
import os
from pathlib import Path
from pandas import read_excel
import pandas

from selenium import webdriver
options = Options()
options.headless = True
start = time.time()
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

module_path = os.path.dirname(os.path.realpath(__file__))
# print(module_path)
parser = argparse.ArgumentParser()
parser.add_argument("file_path", type=Path)
p = parser.parse_args()
fil = p.file_path
filt=str(p.file_path)
filt=filt.replace('.xlsx','')
filepath= f'{filt}+output_files.xlsx'
ic(filepath)
#loc = ("C://senthil-code//freelancer//jay//mycode//List_details.xlsx")
#my_sheet = 'TGT-2234' # change it to your sheet name, you can find your sheet name at the bottom left of your excel file
file_name = module_path+'\\List_details.xlsx' # change it to the name of your excel file
ic(file_name)
#df = read_excel(file_name, sheet_name = my_sheet)
#print(df.head()) # shows headers with top 5 rows
df = read_excel(fil, sheet_name=0, usecols=['BARCODE'])
print(df.head()) # shows headers with top 5 rows
lst = []
lt=[]
lrt=[]
lty=[]
lsst=[]
#def scrape(url, *, loop):
#    ic("scrape first coming here")
    
#    loop.run_in_executor(executor, scraper, url)

def scraper(url):
    ic("scraper second coming here")
    driver.get(url)
    ic(url)
    time.sleep(5)
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        ad=elem.get_attribute("href")
        if '/p/' in ad and '#lnk=sametab' in ad and 'type=scroll_to_review_section' not in ad:
            ic(ad)
            lst.append(ad)
            lsst.append(url)
                        
    end = time.time()
    ic(f"--- {time.time() - start} seconds ---")
            

vals = df.values
#vals=df.head().values
lstu = vals.tolist()

#for url in ["https://www.target.com/s?searchTerm=811138036751","https://www.target.com/s?searchTerm=8809108011091"] :
for url in vals:
    time.sleep(2)
    scraper(f"https://www.target.com/s?searchTerm={str(url)}")

#loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop)))

lt=list(set(lst))
ic(lt)
lrt=list(set(lsst))
ic(lrt)
dff = pd.DataFrame(list(zip(lrt, lt)),
              columns=['URL','URL_LINK'])
pandas.set_option('display.max_colwidth', 40)
dff.to_excel(filepath, index=False)
end = time.time()
print(f"--- {time.time() - start} seconds ---")

driver.quit()
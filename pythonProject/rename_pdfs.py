import datetime
import os as os
import pandas as pd
import shutil, pathlib, time, glob
import xlsxwriter
import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import  expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from tabulate import tabulate

path_files = 'C:\\Users\\hochulir\\Downloads'
foldername = 'LVS_Africa_2021_all+health+ncd_bycountry_1-1'

os.getcwd()
os.listdir(path_files)
df_lvs = pd.read_excel(f'{path_files}/LVS_Africa_2021_all+health+ncd_FINAL.xlsx', sheet_name='MAILMERGE_LVS')
df_lvs.columns
cntry_list = df_lvs.country_name
cntry_list

pdf_list = os.listdir(f'{path_files}/{foldername}')
pdf_list = sorted(pdf_list,key=len)


for i_cntry in cntry_list:
    n_cntry = cntry_list[cntry_list == i_cntry].index[0]
    shutil.move(f'{path_files}/LVS_Africa_2021_all+health+ncd_bycountry_1-1/{pdf_list[n_cntry]}', f'{path_files}/LVS_Africa_2021_all+health+ncd_bycountry_1-1/LVS_Africa_2021_all+health+ncd_{i_cntry}.pdf')


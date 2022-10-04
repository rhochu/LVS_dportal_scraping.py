"""
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
df_cntry_iso = pd.read_json('https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.json')

"""

import json
import requests

key1 = '082d6b1b00da4a12ae5ddfe79c09f6b0'
key2 = 'd8e673a6facd4347a30148c912413cc4'
'082d6b1b00da4a12ae5ddfe79c09f6b0' ==key1


import json
import requests

url = 'https://api.iatistandard.org/datastore/transaction/select?q=(sector_code:11110 OR transaction_sector_code:11110)'
r = requests.get(
    url,
    headers={'Ocp-Apim-Subscription-Key': '082d6b1b00da4a12ae5ddfe79c09f6b0'}
)
data = json.loads(r.text)
import datetime
import numpy as np
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

os.getcwd()
path_files = 'C:\\Users\\hochulir\\Downloads'
name_files = '11 all projects,  all countries to Africa, 2021, DETAILED' #'2 clust_ LifeSc, all countries to Africa, 2021, DETAILED' #'11 all projects,  all countries to Africa, 2021, DETAILED'
os.listdir(path_files)

if name_files == '11 all projects,  all countries to Africa, 2021, DETAILED':  funding_purpose = 'all_'
elif name_files == '2 clust_ LifeSc, all countries to Africa, 2021, DETAILED': funding_purpose = 'health_'
funding_purpose

df_fdi = pd.read_excel(f'{path_files}/{name_files}.xlsx', sheet_name='fDiMarkets')

# change "Capital investment" to actuall millions
df_fdi['Capital investment'] = df_fdi['Capital investment']*1000000
df_fdi['Capital investment']


#create new df for concacatinaion
d = {'country_name': df_cntry_iso['name'][df_cntry_iso['region'] == 'Africa'],
     'iso2': df_cntry_iso['alpha-2'][df_cntry_iso['region'] == 'Africa'],
     'iso3': df_cntry_iso['alpha-3'][df_cntry_iso['region'] == 'Africa'],
     'n_project':0,
     f'fdi_{funding_purpose}USD': np.nan,
     f'fdi_{funding_purpose}names': np.nan}
df_fdi_conc = pd.DataFrame.from_dict(d).reset_index().drop(["index"], axis=1)



# name change necessary to match the unproper naming convetion of fDi Markets
df_fdi_conc.columns
df_fdi_conc['country_name'][df_fdi_conc['country_name'] == 'Tanzania, United Republic of'] = 'Tanzania'
df_fdi_conc['country_name'][df_fdi_conc['country_name'] == 'Congo, Democratic Republic of the'] = 'Democratic Republic of Congo'
df_fdi_conc['country_name'][df_fdi_conc['country_name'] == 'Côte d\'Ivoire'] = 'Cote d Ivoire'



i = 0
for i in range(0, df_fdi_conc.shape[0]):

    i_name = df_fdi_conc['country_name'][i]
    sub_df_fdi = df_fdi[df_fdi['Destination country']==i_name].sort_values(by=f'Capital investment', ascending = False)
    sub_df_fdi
    donor_list = [f'{donor_name} (USD {donor_amount})' for donor_name, donor_amount in
                  zip(sub_df_fdi['Investing company'], round(sub_df_fdi[f'Capital investment']).astype(int))]
    donor_string = '; '.join(donor_list[:100])

    df_fdi_conc['n_project'][df_fdi_conc['country_name'] == df_fdi_conc['country_name'][i]] = sub_df_fdi.shape[0]
    df_fdi_conc[f'fdi_{funding_purpose}USD'][df_fdi_conc['country_name'] == df_fdi_conc['country_name'][i]]     = sub_df_fdi['Capital investment'].sum()
    df_fdi_conc[f'fdi_{funding_purpose}names'][df_fdi_conc['country_name'] == df_fdi_conc['country_name'][i]]     = donor_string


writer = pd.ExcelWriter(f'{path_files}/{name_files}_concatPY.xlsx', engine='xlsxwriter')
df_fdi.to_excel(writer, sheet_name= 'fDiMarkets', index=False)
df_fdi_conc.to_excel(writer, sheet_name= 'concatinated_data_by_python', index=False)
writer.save()
time.sleep(1)
writer.close()



print(tabulate(df_fdi, headers='keys', tablefmt='psql'))

print(tabulate(df_fdi_conc, headers='keys', tablefmt='psql'))

print('done script')
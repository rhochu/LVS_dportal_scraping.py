
import time, datetime
import os as os
import pandas as pd

import json, requests

"""
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
"""
df_cntry_iso = pd.read_json('https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.json')
str_iso2_all_country = ' '.join(df_cntry_iso[df_cntry_iso['region']=='Africa']['alpha-2'])

os.getcwd()
os.listdir('C:\\Users\\hochulir\\Desktop')
auth_txt = open('C:\\Users\\hochulir\\Desktop\\iati_api_auth.txt','r').read()
auth_dict = json.loads(auth_txt)
auth_key1 = auth_dict['iati_key1']



str_native = '122 121 130 123'
str_qurl=str_native.replace('"','%22').replace(' ', '%20').replace(':', '%3A').replace(',', '%2C').replace('[','%5B').replace(']','%5D')
print(str_qurl)

q_county2 = 'DZ%20AO%20BJ%20BW%20IO%20BF'# %20BI%20CV%20CM%20CF%20TD%20KM%20CG%20CD%20CI%20DJ%20EG%20GQ%20ER%20SZ%20ET%20TF%20GA%20GM%20GH%20GN%20GW%20KE%20LS%20LR%20LY%20MG%20MW%20ML%20MR%20MU%20YT%20MA%20MZ%20NA%20NE%20NG%20RE%20RW%20SH%20ST%20SN%20SC%20SL%20SO%20ZA%20SS%20SD%20TZ%20TG%20TN%20UG%20EH%20ZM%20ZW'
q_sector = '122%20121%20130%20123'

url = 'https://api.iatistandard.org/datastore/transaction/select?' \
      'q=' \
      f'(recipient_country_code%3A({q_county2})' \
      f'%20OR%20' \
      f'transaction_recipient_country_code%3A({q_county2}))'\
      f'%20AND%20' \
      f'(transaction_sector_code%3A({q_sector}))' \
      f'%20AND%20' \ 
      f'transaction_value_value_date%3A%5B2021-01-01T00%3A00%3A00Z%20TO%202021-12-31T00%3A00%3A00Z%5D' \
      f'&rows=998' \
      f'&wt=json'

r = requests.get(
    url,
    headers={'Ocp-Apim-Subscription-Key': f'{auth_key1}'},
    verify= False
)

data = json.loads(r.text)
resp_head = data['responseHeader']
resp_head
resp = data['response']
resp['numFound']
resp['start']
resp['numFoundExact']

docs = resp['docs']

selected_doc_list = []
item  = docs[0]
for item in docs:
    transaction_value = item['transaction_value']
    transaction_value_currency = item['transaction_value_currency']
    transaction_sector_code = item['transaction_sector_code']
    transaction_description_narrative = item['transaction_description_narrative']
    transaction_provider_org_narrative = item['transaction_provider_org_narrative']
    transaction_transaction_date_iso_date = item['transaction_transaction_date_iso_date']
    description_narrative = item['description_narrative']
    recipient_country_code = item['recipient_country_code']
    reporting_org_narrative = item['reporting_org_narrative']

    selected_doc_item = {

        'transaction_value': transaction_value,
        'transaction_value_currency': transaction_value_currency,
        'transaction_sector_code': transaction_sector_code,
        'transaction_description_narrative': transaction_description_narrative,
        'transaction_provider_org_narrative': transaction_provider_org_narrative,
        'transaction_transaction_date_iso_date': transaction_transaction_date_iso_date,
        'description_narrative': description_narrative,
        'recipient_country_code' : recipient_country_code,
        'reporting_org_narrative': reporting_org_narrative
        }
    selected_doc_list.append(selected_doc_item)


print(selected_doc_list)
type(selected_doc_list)

df_selected_doc = pd.DataFrame(selected_doc_list)

writer = pd.ExcelWriter(f'C:\\Users\\hochulir\\Desktop\\API_export.xlsx', engine='xlsxwriter')
df_selected_doc.to_excel(writer, sheet_name= 'api_export', index=False)
writer.save()
time.sleep(1)
writer.close()



print(item['recipient_country_code'])
len(data)
type(data)
data

data.keys()
data['error']

data.keys()
resp_head
resp

resp.keys()
type(docs[0])
docs[0]
docs[6]
docs[999]

docs[0].keys()
['transaction_value', 'transaction_sector_code', 'transaction_humanitarian', 'transaction_value_currency', 'transaction_value_value_date', 'transaction_sector_vocabulary', 'transaction_description_narrative', 'transaction_transaction_type_code', 'transaction_provider_org_narrative', 'transaction_transaction_date_iso_date', 'xml_lang', 'humanitarian', 'dataset_version', 'iati_identifier', 'title_narrative', 'default_currency', 'contact_info_type', 'document_link_url', 'reporting_org_ref', 'activity_date_type', 'contact_info_email', 'reporting_org_type', 'activity_status_code', 'contact_info_website', 'document_link_format', 'default_aid_type_code', 'description_narrative', 'last_updated_datetime', 'participating_org_ref', 'activity_date_iso_date', 'default_flow_type_code', 'participating_org_role', 'participating_org_type', 'recipient_country_code', 'collaboration_type_code', 'reporting_org_narrative', 'default_finance_type_code', 'dataset_generated_datetime', 'document_link_category_code', 'document_link_language_code', 'participating_org_narrative', 'recipient_country_narrative', 'document_link_title_narrative', 'contact_info_job_title_narrative', 'contact_info_person_name_narrative', 'contact_info_organisation_narrative', 'document_link_description_narrative', 'document_link_document_date_iso_date']


len(docs)
docs.keys()
docs[0]



df=pd.DataFrame(docs)
df
# print(tabulate(df, headers='keys', tablefmt='psql'))

df['transaction_value_value_date'].value_counts().sort_values()
df['transaction_value_value_date'].sort_values()






for n in range(0,3123, 999 ):
    print(n)

"""
'q=(' \
'sector_code%3A11130' \
'%20OR%20' \
'transaction_sector_code%3A11130)' \
'%20AND%20' \
'(recipient_country_code%3A(UG%20KE)%20OR%20transaction_recipient_country_code%3A(UG%20KE))%20AND%20activity_date_iso_date%3A%5B2021-01-01T00%3A00%3A00Z%20TO%20*%5D&rows=300&wt=json&fl=participating_org_ref%2Cparticipating_org_narrative
"""



#questions fofana
"""
- how bad is it to not use safety certificate? > how to run with ssl?
- how to get "codelist" that shows which query keys can be used? > just take it from the record of a random response?
- can I use key value pairs from the regular search in the API call?
>> 
# https://www.programiz.com/python-programming/online-compiler/ =>>> solves the issue with the SSL certificate, apparently a ROCHE system issue.
"""
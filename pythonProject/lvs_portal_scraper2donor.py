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



def dportal_scraper(dp_cntry, dp_sect_full, dp_stat, dp_y_min, dp_y_max, dp_y_view, dp_filename_suffix, path_dwnlds, path_csv_dmp):
    timer_start = datetime.datetime.now()
    for i_cntry in dp_cntry:
        for i_sttngs in range(0, len(dp_sect_full)):

            if os.path.isfile(f'{path_dwnlds}/dportal_donors_{i_cntry}.csv'):
                os.remove(f'{path_dwnlds}/dportal_donors_{i_cntry}.csv')
            else:
                print(f'no <<dportal_donors>> file found')

            if not os.path.exists(f'{path_csv_dmp}'):
                os.mkdir(f'{path_csv_dmp}')
                print(f'dir <<scaper_dump>> created')
            else:
                print(f'dir <<scaper_dump>> exists')

            #print(f'country {dp_cntry[i_cntry]} ({i_cntry} of {len(dp_cntry)}), setting: {i_sttngs}')

            scrape_URL = f'https://d-portal.org/ctrack.html?country_code={i_cntry}{dp_sect_full[i_sttngs]}&status_code={dp_stat[i_sttngs]}&year_min={dp_y_min[i_sttngs]}&year_max={dp_y_max[i_sttngs]}#view=donors&year={dp_y_view[i_sttngs]}'
            print(scrape_URL)
            s = Service('C:/Users/hochulir/PycharmProjects/pythonProject/chromedriver.exe')
            driver = webdriver.Chrome(service = s)
            driver.get(scrape_URL)
            time.sleep(3)
            try:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'CSV')))
                print("Page is ready!")
                element.click()

            except TimeoutException:
                print("Loading took too much time!")

            time.sleep(3)
            shutil.move(f'{path_dwnlds}/dportal_donors_{i_cntry}.csv',f'{path_csv_dmp}/{i_cntry}_{dp_filename_suffix[i_sttngs]}_{dp_y_view[i_sttngs]}.csv' )
            driver.quit()
            print(f'file for <{i_cntry}_{dp_filename_suffix[i_sttngs]}_{dp_y_view[i_sttngs]}> successfully exported ')

    timer_end = datetime.datetime.now()
    timer_total = timer_end - timer_start

    lines = [f'time stamp d-portal scraper, run at: {datetime.datetime.now()}', f'runtime: {timer_total} h:m:s',
             f'> scraper settings:', f'selected countries: {dp_cntry}', f'selected sectors: {dp_sect_full}',
             f'project status: {dp_stat}', f'time range year start: {dp_y_min}', f'time range year start: {dp_y_max}',
             f'year set focus: {dp_y_view}', f'filename suffix: {dp_filename_suffix}',
             f'path "downloads" directory: {path_dwnlds}', f'path "data" directory (moved to): {path_csv_dmp}', ' ']

    with open(f'{path_csv_dmp}/0_timestamp.txt', 'w') as f:
        f.write('\n')
        for line in lines:
            f.write(line)
            f.write('\n')

def merge_csvs(xlsx_file_name, path_csv_dmp):
    timer_start = datetime.datetime.now()
    if not os.path.exists(f'{path_csv_dmp}'):
        print(f'Run scraper first! No csvs to merge')
    else:
        csv_names_dmp = glob.glob(f'{path_csv_dmp}/*.csv')

        writer = pd.ExcelWriter(f'{path_csv_dmp}/{xlsx_file_name}_RAW.xlsx', engine='xlsxwriter')
        for i_csv_name in csv_names_dmp:
            dp_cntry_full = list(df_cntry_iso['name'][df_cntry_iso['alpha-2'] == i_csv_name[43:45]])[0]
            df_csv = pd.read_csv(i_csv_name, thousands=',')
            df_csv.insert(0, f'country_iso2', f'{i_csv_name[43:45]}')
            df_csv.insert(0, f'country_name', f'{dp_cntry_full}')

            df_csv.to_excel(writer, sheet_name=i_csv_name[43:-4], index = False)
            print(f'write to XSLX_RAW > {i_csv_name[43:-4]}')
            del df_csv
            # shutil.move(f'{i_csv_name}',f'{path_csv_dmp}/dportal_csv_exports')
        print(f' >> xlsx merge for RAW csv finished successfully')
        writer.save()
        time.sleep(1)
        writer.close()

        writer = pd.ExcelWriter(f'{path_csv_dmp}/{xlsx_file_name}_BY_FUNDERS.xlsx', engine='xlsxwriter')
        df_byfunder_conc = pd.DataFrame()
        for i_csv_name in csv_names_dmp:
            dp_cntry_full = list(df_cntry_iso['name'][df_cntry_iso['alpha-2'] == i_csv_name[43:45]])[0]
            df_csv = pd.read_csv(i_csv_name, thousands=',')
            df_byfunder = df_csv.groupby('reporting-org')['total-spend'].sum().to_frame().sort_values(by='total-spend', ascending=False)
            df_byfunder.reset_index(inplace = True)
            df_byfunder = df_byfunder.rename(columns = {'index': 'reporting-org'})
            df_byfunder.insert(0, f'country_iso2', f'{i_csv_name[43:45]}')
            df_byfunder.insert(0, f'country_name', f'{dp_cntry_full}')
            df_byfunder.insert((df_byfunder.columns.get_loc('total-spend')+1), f'currency', f'USD')

            df_byfunder_conc = pd.concat([df_byfunder_conc, df_byfunder])
            df_byfunder_conc.to_excel(writer, sheet_name='byfunder', index = False)
            # df_byfunder.to_excel(writer, sheet_name=i_csv_name[43:-4], index = False)
            print(f'write to XSLX_BY_FUNDER > {i_csv_name[43:-4]}')
            del df_csv, df_byfunder

        print(f' >> xlsx merge for BY FUNDER csv finished successfully')
        writer.save()
        time.sleep(1)
        writer.close()

        timer_end = datetime.datetime.now()
        timer_total = timer_end - timer_start

        lines = [f'time stamp merge CSVs (one sector selected), run at: {datetime.datetime.now()}', f'runtime: {timer_total} h:m:s']
        with open(f'{path_csv_dmp}/0_timestamp.txt', 'a') as f:
            f.write('\n')
            for line in lines:
                f.write(line)
                f.write('\n')

def merge_csvs_multi_sector(xlsx_file_name, path_csv_dmp, dp_filename_suffix):
    timer_start = datetime.datetime.now()
    if not os.path.exists(f'{path_csv_dmp}'):
        print(f'Run scraper first! No csvs to merge')
    else:
        csv_names_dmp = glob.glob(f'{path_csv_dmp}/*.csv')

        writer = pd.ExcelWriter(f'{path_csv_dmp}/{xlsx_file_name}_RAW.xlsx', engine='xlsxwriter')
        for i_csv_name in csv_names_dmp:
            dp_cntry_full = list(df_cntry_iso['name'][df_cntry_iso['alpha-2'] == i_csv_name[67:69]])[0]
            df_csv = pd.read_csv(i_csv_name, thousands=',')
            df_csv.insert(0, f'country_iso2', f'{i_csv_name[67:69]}')
            df_csv.insert(0, f'country_name', f'{dp_cntry_full}')

            df_csv.to_excel(writer, sheet_name=i_csv_name[67:-4], index = False)
            print(f'write to XSLX_RAW > {i_csv_name[67:-4]}')
            del df_csv
            # shutil.move(f'{i_csv_name}',f'{path_csv_dmp}/dportal_csv_exports')
        print(f' >> xlsx merge for RAW csv finished successfully')
        writer.save()
        time.sleep(1)
        writer.close()

        #i_sector_name = dp_filename_suffix[0]
        #i_csv_name_bysec = csv_name_dmp_bysec[0]
        writer = pd.ExcelWriter(f'{path_csv_dmp}/{xlsx_file_name}_MERGED.xlsx', engine='xlsxwriter')
        for i_sector_name in dp_filename_suffix:
            csv_name_dmp_bysec = glob.glob(f'{path_csv_dmp}/*_{i_sector_name}_*.csv')
            df_byfunder_conc = pd.DataFrame()

            for i_csv_name_bysec in csv_name_dmp_bysec:
                dp_cntry_full = list(df_cntry_iso['name'][df_cntry_iso['alpha-2'] == i_csv_name_bysec[67:69]])[0]
                df_csv = pd.read_csv(i_csv_name_bysec, thousands=',')
                df_byfunder = df_csv.sort_values(by = f't2021', ascending= False)
                #df_byfunder = df_csv.groupby('reporting-org')['total-spend'].sum().to_frame().sort_values(by='total-spend', ascending=False)
                #df_byfunder.reset_index(inplace=True)
                #df_byfunder = df_byfunder.rename(columns={'index': 'reporting-org'})
                df_byfunder.insert(0, f'd-portal name setting', f'{i_csv_name_bysec[70:-4]}')
                df_byfunder.insert(0, f'country_iso2', f'{i_csv_name_bysec[67:69]}')
                df_byfunder.insert(0, f'country_name', f'{dp_cntry_full}')
                df_byfunder.insert((df_byfunder.columns.get_loc('b2023') + 1), f'currency', f'USD')

                df_byfunder_conc = pd.concat([df_byfunder_conc, df_byfunder])
                print(f'write to XSLX_MERGED > {i_csv_name_bysec[67:-4]}')
                del df_csv, df_byfunder

            df_byfunder_conc.to_excel(writer, sheet_name=f'{i_sector_name}', index=False)
            del df_byfunder_conc

        print(f' >> xlsx merge for BY FUNDER csv finished successfully')
        writer.save()
        time.sleep(1)
        writer.close()
    print(f'xlsx merge for BY FUNDER BY SECTOR csv finished successfully')

    shutil.copyfile(f'{path_csv_dmp}/{xlsx_file_name}_MERGED.xlsx', f'{path_csv_dmp_lvs[:-17]}/{xlsx_file_name}_MERGED.xlsx')

    timer_end = datetime.datetime.now()
    timer_total = timer_end - timer_start

    lines = [f'time stamp merge CSVs (multiple sectors), run at: {datetime.datetime.now()}', f'runtime: {timer_total} h:m:s']
    with open(f'{path_csv_dmp}/0_timestamp.txt', 'a') as f:
        f.write('\n')
        for line in lines:
            f.write(line)
            f.write('\n')



# driver setup LVS
cntry_Africa_ALL = list(df_cntry_iso['alpha-2'][df_cntry_iso.region.isin(['Africa'])])
cntry_Africa_selection = ['NG', 'GH', 'ZA', 'DZ', 'MA', 'TN', 'LY', 'CD', 'CG', 'GA', 'CF', 'CM', 'TD', 'ER', 'TZ', 'ET', 'UG', 'RW', 'SO']
dp_cntry_lvs = cntry_Africa_ALL[:2]# cntry_Africa_selection[0:1]

dp_sect_full_lvs = ['', '&sector_group=122%2C121%2C123%2C130']
dp_stat_lvs =  ['3%2C2%2C1', '3%2C2%2C1']
dp_y_min_lvs = ['2021', '2021']
dp_y_max_lvs = ['2023', '2023']
dp_y_view_lvs = ['2021', '2021']
dp_filename_suffix_lvs = ['all', 'health']

xlsx_file_name_lvs = '0_dportal_LVS'
path_dwnlds_lvs = 'C:/Users/hochulir/Downloads'
path_csv_dmp_lvs = 'G:/My Drive/1_LandscapingValueStreams Africa/data/scraper_csv_dump'


# driver setup Estefani Bello
dp_cntry_EB = ['HN', 'SV', 'BO', 'NI', 'VN', 'ID', 'PH', 'EG', 'BD', 'IN', 'PK', 'NG', 'KE', 'MA', 'TN', 'CI', 'GH']
dp_sect_full_EB = ['&sector_group=123']
dp_stat_EB =  ['3%2C2%2C1']
dp_y_min_EB = ['2021']
dp_y_max_EB = ['2023']
dp_y_view_EB = ['2021']
dp_filename_suffix_EB = ['NCD']

xlsx_file_name_EB = '0_dportal_estefBELLO'
path_dwnlds_EB = 'C:/Users/hochulir/Downloads'
path_csv_dmp_EB = 'G:/My Drive/1_LandscapingValueStreams Africa/data/scraper_csv_dump'




# RUN SCRAPER
dportal_scraper(dp_cntry_lvs, dp_sect_full_lvs, dp_stat_lvs, dp_y_min_lvs, dp_y_max_lvs, dp_y_view_lvs, dp_filename_suffix_lvs, path_dwnlds_lvs, path_csv_dmp_lvs)
merge_csvs_multi_sector(xlsx_file_name_lvs, path_csv_dmp_lvs, dp_filename_suffix_lvs)

#dportal_scraper(dp_cntry_EB, dp_sect_full_EB, dp_stat_EB, dp_y_min_EB, dp_y_max_EB, dp_y_view_EB, dp_filename_suffix_EB, path_dwnlds_EB, path_csv_dmp_EB)
#merge_csvs_multi_sector(xlsx_file_name_EB, path_csv_dmp_EB, dp_filename_suffix_EB)



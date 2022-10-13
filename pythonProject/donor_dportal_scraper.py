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


# variables for function testing
"""
cntry_Africa_ALL = list(df_cntry_iso['alpha-2'][df_cntry_iso.region.isin(['Africa'])])
dp_cntry = dp_cntry_run1 # cntry_Africa_selection[0:1]
dp_sect_full = dp_sect_full_run1
dp_stat = dp_stat_run1
dp_filename_suffix = dp_filename_suffix_run1
path_dwnlds = path_dwnlds_run1
path_csv_dmp = path_csv_dmp_run1

dp_y_min =  dp_y_min_run1
dp_y_max= dp_y_max_run1
dp_y_view =dp_y_view_run1

xlsx_file_name = xlsx_file_name_run1
y_focus = y_focus_run1
strname_cntry_separators = strname_cntry_separators_run1
"""

def dportal_scraper(dp_cntry, dp_sect_full, dp_stat, dp_y_min, dp_y_max, dp_y_view, dp_filename_suffix, path_dwnlds, path_csv_dmp):
    timer_start = datetime.datetime.now()
    i_counter = 0
    i_cntry = dp_cntry[0]
    for i_cntry in dp_cntry:
        i_sttngs = range(0, len(dp_sect_full))[0]
        for i_sttngs in range(0, len(dp_sect_full)):
            if os.path.isfile(f'{path_dwnlds}/dportal_donors_{i_cntry}.csv'):
                os.remove(f'{path_dwnlds}/dportal_donors_{i_cntry}.csv')

            if not os.path.exists(f'{path_csv_dmp}'):
                os.mkdir(f'{path_csv_dmp}')
            else:
                print(f'dir <<scaper_dump>> exists')

            scrape_URL = f'https://d-portal.org/ctrack.html?country_code={i_cntry}{dp_sect_full[i_sttngs]}&status_code={dp_stat[i_sttngs]}&year_min={dp_y_min[i_sttngs]}&year_max={dp_y_max[i_sttngs]}#view=donors&year={dp_y_view[i_sttngs]}'
            #print(scrape_URL)
            s = Service('C:/Users/hochulir/PycharmProjects/pythonProject/chromedriver.exe')
            driver = webdriver.Chrome(service = s)
            driver.get(scrape_URL)
            time.sleep(2)
            try:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'CSV')))

                element.click()

            except TimeoutException:
                print("Loading took too much time!")

            time.sleep(2)
            shutil.move(f'{path_dwnlds}/dportal_donors_{i_cntry}.csv',f'{path_csv_dmp}/{i_cntry}_{dp_filename_suffix[i_sttngs]}_{dp_y_view[i_sttngs]}.csv' )

            driver.quit()
            i_counter = i_counter+1
            loadingbarTO40 = round(i_counter / (len(dp_cntry) * len(dp_sect_full))*40)

            print(f'{i_cntry}, {i_counter} of {len(dp_cntry)*len(dp_sect_full)} scraped ; '
                  f'|{("="*loadingbarTO40) +"|"+("."*(40- loadingbarTO40))}|'
                  f'<{i_cntry}_{dp_filename_suffix[i_sttngs]}_{dp_y_view[i_sttngs]}>')


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


def merge_csvs_multi_sector(xlsx_file_name, path_csv_dmp, dp_filename_suffix, y_focus, strname_cntry_separators):
    timer_start = datetime.datetime.now()
    if not os.path.exists(f'{path_csv_dmp}'):
        print(f'Run scraper first! No csvs to merge')
    else:
        writer = pd.ExcelWriter(f'{path_csv_dmp}/{xlsx_file_name}_MERGED.xlsx', engine='xlsxwriter')

        i_sector_name = dp_filename_suffix[0]
        for i_sector_name in dp_filename_suffix:
            csv_name_dmp_bysec = glob.glob(f'{path_csv_dmp}/*_{i_sector_name}_*.csv')
            df_byfunder_conc = pd.DataFrame()

            i_csv_name_bysec = csv_name_dmp_bysec[0]
            for i_csv_name_bysec in csv_name_dmp_bysec:
                dp_cntry_full = list(df_cntry_iso['name'][df_cntry_iso['alpha-2'] == i_csv_name_bysec[strname_cntry_separators[0]:strname_cntry_separators[1]]])[0]
                df_csv = pd.read_csv(i_csv_name_bysec, thousands=',')
                df_byfunder = df_csv.sort_values(by = f't{i_csv_name_bysec[-8:-4]}', ascending= False)
                #df_byfunder = df_csv.groupby('reporting-org')['total-spend'].sum().to_frame().sort_values(by='total-spend', ascending=False)
                #df_byfunder.reset_index(inplace=True)
                #df_byfunder = df_byfunder.rename(columns={'index': 'reporting-org'})
                df_byfunder.insert(0, f'subregion', f'{df_cntry_iso["sub-region"][df_cntry_iso["alpha-2"] == i_csv_name_bysec[strname_cntry_separators[0]:strname_cntry_separators[1]]].iat[0]}')
                df_byfunder.insert(0, f'region', f'{df_cntry_iso["region"][df_cntry_iso["alpha-2"] == i_csv_name_bysec[strname_cntry_separators[0]:strname_cntry_separators[1]]].iat[0]}')
                df_byfunder.insert(0, f'sector_name', f'{i_csv_name_bysec[strname_cntry_separators[1]+1:-9]}')
                df_byfunder.insert(0, f'year_focus', f'{i_csv_name_bysec[-8:-4]}')
                df_byfunder.insert(0, f'country_iso2', f'{i_csv_name_bysec[strname_cntry_separators[0]:strname_cntry_separators[1]]}')
                df_byfunder.insert(0, f'country_name', f'{dp_cntry_full}')
                df_byfunder.insert((df_byfunder.columns.get_loc(f'b{str(int(i_csv_name_bysec[-8:-4])+2)}') + 1), f'currency', f'USD')

                df_byfunder.columns
                df_byfunder.columns = ['country_name', 'country_iso2',  'year_focus', 'sector_name', 'region', 'subregion', 'crs', 'donor', 'transaction_y-2', 'transaction_y-1', 'transaction_year_focus', 'budget_y+1', 'budget_y+2', 'currency']

                df_byfunder_conc = pd.concat([df_byfunder_conc, df_byfunder])
                print(f'write to XSLX_MERGED > {i_csv_name_bysec[strname_cntry_separators[0]:-4]}')
                del df_csv, df_byfunder

            #df_byfunder_conc.to_excel(writer, sheet_name=f'{i_sector_name}', index=False)
            df_byfunder_conc.to_excel(writer, sheet_name=f'dportal_export', index=False)

            del df_byfunder_conc

        print(f' >> xlsx merge for BY FUNDER csv finished successfully')
        writer.save()
        time.sleep(1)
        writer.close()
    print(f'xlsx merge for BY FUNDER BY SECTOR csv finished successfully')

    #shutil.copyfile(f'{path_csv_dmp}/{xlsx_file_name}_MERGED.xlsx', f'{path_csv_dmp[:-16]}/{xlsx_file_name}_MERGED.xlsx')

    timer_end = datetime.datetime.now()
    timer_total = timer_end - timer_start

    lines = [f'time stamp merge CSVs (multiple sectors), run at: {datetime.datetime.now()}', f'runtime: {timer_total} h:m:s']
    with open(f'{path_csv_dmp}/0_timestamp.txt', 'a') as f:
        f.write('\n')
        for line in lines:
            f.write(line)
            f.write('\n')




# Focus Africa 2021 - run1

cntry_Africa_ALL = list(df_cntry_iso['alpha-2'][df_cntry_iso.region.isin(['Africa'])])
dp_cntry_run1 = cntry_Africa_ALL[0:2]  # cntry_Africa_selection[0:1]
dp_cntry_run1 = df_cntry_iso['alpha-2']
dp_sect_full_run1 = ['', '&sector_group=122%2C121%2C123%2C130', '&sector_group=123']
dp_stat_run1 = ['3%2C2%2C1', '3%2C2%2C1', '3%2C2%2C1']
dp_filename_suffix_run1 = ['all', 'health', 'ncd']
path_dwnlds_run1 = 'C:/Users/hochulir/Downloads'
path_csv_dmp_run1 = 'C:/Users/hochulir/Desktop/scraper_csv_dump'#'G:/My Drive/1_LandscapingValueStreams Africa/data_donors/scraper_csv_dmp'
dp_y_min_run1 =  ['2021'] *len(dp_filename_suffix_run1)
dp_y_max_run1 =  ['2022'] *len(dp_filename_suffix_run1)
dp_y_view_run1 = ['2021'] *len(dp_filename_suffix_run1)

xlsx_file_name_run1 = '0_dportal_LVS_all_health_ncd_World_2021'
y_focus_run1 = '2021'
#glob.glob(f'{path_csv_dmp_run1}/*_{dp_filename_suffix_run1[0]}_*.csv')[0] # ATTENTION: Last two digits must be set in such a way that it gives a iso2 country code.
strname_cntry_separators_run1 = [43,45]


dportal_scraper(dp_cntry_run1,
                dp_sect_full_run1,
                dp_stat_run1,
                dp_y_min_run1,
                dp_y_max_run1,
                dp_y_view_run1,
                dp_filename_suffix_run1,
                path_dwnlds_run1,
                path_csv_dmp_run1)

merge_csvs_multi_sector(xlsx_file_name_run1,
                        path_csv_dmp_run1,
                        dp_filename_suffix_run1,
                        y_focus_run1,
                        strname_cntry_separators_run1)

shutil.move(f'{path_csv_dmp_run1}', f'{path_csv_dmp_run1}_LVS_{"_".join(dp_filename_suffix_run1)}_{y_focus_run1}')

dp_filename_suffix_run1.join


# Focus Africa past 40 years
run_ts_scraper = False
if run_ts_scraper:
    i_time_series = 2008
    for i_time_series in range(2008, 2008):  # 1993 - 2008
        print(i_time_series)

        cntry_Africa_ALL = list(df_cntry_iso['alpha-2'][df_cntry_iso.region.isin(['Africa'])])

        dp_cntry_lvs = cntry_Africa_ALL  # cntry_Africa_selection[0:1]
        dp_sect_full_lvs = ['', '&sector_group=122%2C121%2C123%2C130', '&sector_group=123']
        dp_stat_lvs = ['3%2C2%2C1', '3%2C2%2C1', '3%2C2%2C1']
        dp_y_min_lvs = [f'{i_time_series}', f'{i_time_series}', f'{i_time_series}']  # ['2021', '2021', '2021']
        dp_y_max_lvs = [f'{i_time_series + 1}', f'{i_time_series + 1}',
                        f'{i_time_series + 1}']  # ['2022', '2022', '2022']
        dp_y_view_lvs = [f'{i_time_series}', f'{i_time_series}', f'{i_time_series}']  # ['2021', '2021', '2021']
        dp_filename_suffix_lvs = ['all', 'health', 'ncd']
        path_dwnlds_lvs = '/Users/raulhochuli/Downloads'  # 'C:/Users/hochulir/Downloads'
        path_csv_dmp_lvs = '/Users/raulhochuli/Desktop'  # 'G:/My Drive/1_LandscapingValueStreams Africa/data/scraper_csv_dmp'

        xlsx_file_name_lvs2021 = '0_dportal_Africa_2021_all_health_ncd'
        y_focus_lvs = [f'{i_time_series}']
        folder_rename_dmp = ' Africa'

        dportal_scraper(dp_cntry_lvs, dp_sect_full_lvs, dp_stat_lvs, dp_y_min_lvs, dp_y_max_lvs, dp_y_view_lvs,
                        dp_filename_suffix_lvs, path_dwnlds_lvs, path_csv_dmp_lvs)

    # merge_csvs_multi_sector(xlsx_file_name_lvs2021, path_csv_dmp_lvs, dp_filename_suffix_lvs, y_focus_lvs )
    # shutil.move(f'{path_csv_dmp_lvs}', f'{path_csv_dmp_lvs}_Africa_{y_focus_lvs2021}')
elif not run_ts_scraper:
    print('> skip time series scraping')




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
cntry_Africa_ALL = list(df_cntry_iso['alpha-2'][df_cntry_iso.region.isin(['Africa'])])

dp_cntry = dp_cntry_lvs  # cntry_Africa_selection[0:1]
dp_sect_full = dp_sect_full_lvs
dp_stat = dp_stat_lvs
dp_filename_suffix = dp_filename_suffix_lvs
path_dwnlds = 'C:/Users/hochulir/Downloads'
path_csv_dmp = 'G:/My Drive/1_LandscapingValueStreams Africa/data/scraper_csv_dmp'
dp_y_min =  dp_y_min_lvs2021
dp_y_max= dp_y_max_lvs2021
dp_y_view =dp_y_view_lvs2021
xlsx_file_name = '0_dportal_LVS_health_Africa_2021'
y_focus = '2021'
"""

def dportal_scraper(dp_cntry, dp_sect_full, dp_stat, dp_y_min, dp_y_max, dp_y_view, dp_filename_suffix, path_dwnlds, path_csv_dmp):
    timer_start = datetime.datetime.now()
    i_counter = 0
    i_cntry = dp_cntry[0]
    for i_cntry in dp_cntry:
        i_sttngs =  range(0, len(dp_sect_full))[2]
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
            print(f'{i_counter} of {len(dp_cntry)*len(dp_sect_full)} scraped ; |{("="*i_counter)+"|"+("."*(len(dp_cntry)*len(dp_sect_full) - i_counter))}| <{i_cntry}_{dp_filename_suffix[i_sttngs]}_{dp_y_view[i_sttngs]}>')



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


def merge_csvs_multi_sector(xlsx_file_name, path_csv_dmp, dp_filename_suffix, y_focus):
    timer_start = datetime.datetime.now()
    if not os.path.exists(f'{path_csv_dmp}'):
        print(f'Run scraper first! No csvs to merge')
    else:
        csv_names_dmp = glob.glob(f'{path_csv_dmp}/*.csv')

        writer = pd.ExcelWriter(f'{path_csv_dmp}/{xlsx_file_name}_RAW.xlsx', engine='xlsxwriter')
        i_csv_name = csv_names_dmp[0]
        for i_csv_name in csv_names_dmp:
            dp_cntry_full = list(df_cntry_iso['name'][df_cntry_iso['alpha-2'] == i_csv_name[66:68]])[0]
            df_csv = pd.read_csv(i_csv_name, thousands=',')
            df_csv.insert(0, f'country_iso2', f'{i_csv_name[66:68]}')
            df_csv.insert(0, f'country_name', f'{dp_cntry_full}')

            df_csv.to_excel(writer, sheet_name=i_csv_name[66:-4], index = False)
            print(f'write to XSLX_RAW > {i_csv_name[66:-4]}')
            del df_csv
            # shutil.move(f'{i_csv_name}',f'{path_csv_dmp}/dportal_csv_exports')
        print(f' >> xlsx merge for RAW csv finished successfully')
        writer.save()
        time.sleep(1)
        writer.close()

        #i_sector_name = dp_filename_suffix[0]
        #i_csv_name_bysec = csv_name_dmp_bysec[0]
        writer = pd.ExcelWriter(f'{path_csv_dmp}/{xlsx_file_name}_MERGED.xlsx', engine='xlsxwriter')

        i_sector_name = dp_filename_suffix[0]
        for i_sector_name in dp_filename_suffix:
            csv_name_dmp_bysec = glob.glob(f'{path_csv_dmp}/*_{i_sector_name}_*.csv')
            df_byfunder_conc = pd.DataFrame()

            i_csv_name_bysec = csv_name_dmp_bysec[0]
            for i_csv_name_bysec in csv_name_dmp_bysec:
                dp_cntry_full = list(df_cntry_iso['name'][df_cntry_iso['alpha-2'] == i_csv_name_bysec[66:68]])[0]
                df_csv = pd.read_csv(i_csv_name_bysec, thousands=',')
                df_byfunder = df_csv.sort_values(by = f't{y_focus}', ascending= False)
                #df_byfunder = df_csv.groupby('reporting-org')['total-spend'].sum().to_frame().sort_values(by='total-spend', ascending=False)
                #df_byfunder.reset_index(inplace=True)
                #df_byfunder = df_byfunder.rename(columns={'index': 'reporting-org'})
                df_byfunder.insert(0, f'd-portal name setting', f'{i_csv_name_bysec[69:-4]}')
                df_byfunder.insert(0, f'country_iso2', f'{i_csv_name_bysec[66:68]}')
                df_byfunder.insert(0, f'country_name', f'{dp_cntry_full}')
                df_byfunder.insert((df_byfunder.columns.get_loc(f'b{str(int(y_focus)+2)}') + 1), f'currency', f'USD')


                df_byfunder_conc = pd.concat([df_byfunder_conc, df_byfunder])
                print(f'write to XSLX_MERGED > {i_csv_name_bysec[66:-4]}')
                del df_csv, df_byfunder

            df_byfunder_conc.to_excel(writer, sheet_name=f'{i_sector_name}', index=False)
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



#General Scraper Setup
# Focus Africa
i_time_series = 2008
for i_time_series in range(2008, 2008): #1993 - 2008
    print(i_time_series)

    cntry_Africa_ALL = list(df_cntry_iso['alpha-2'][df_cntry_iso.region.isin(['Africa'])])

    dp_cntry_lvs = cntry_Africa_ALL  # cntry_Africa_selection[0:1]
    dp_sect_full_lvs = ['', '&sector_group=122%2C121%2C123%2C130', '&sector_group=123']
    dp_stat_lvs =  ['3%2C2%2C1', '3%2C2%2C1', '3%2C2%2C1']
    dp_y_min_lvs = [f'{i_time_series}', f'{i_time_series}', f'{i_time_series}']             # ['2021', '2021', '2021']
    dp_y_max_lvs = [f'{i_time_series +1}', f'{i_time_series +1}', f'{i_time_series +1}']    # ['2022', '2022', '2022']
    dp_y_view_lvs = [f'{i_time_series}', f'{i_time_series}', f'{i_time_series}']            # ['2021', '2021', '2021']
    dp_filename_suffix_lvs = ['all', 'health', 'ncd']
    path_dwnlds_lvs = '/Users/raulhochuli/Downloads'  # 'C:/Users/hochulir/Downloads'
    path_csv_dmp_lvs = '/Users/raulhochuli/Desktop'   # 'G:/My Drive/1_LandscapingValueStreams Africa/data/scraper_csv_dmp'

    xlsx_file_name_lvs2021 = '0_dportal_Africa_2021_all_health_ncd'
    y_focus_lvs = [f'{i_time_series}']
    folder_rename_dmp = ' Africa'

    dportal_scraper(dp_cntry_lvs, dp_sect_full_lvs, dp_stat_lvs, dp_y_min_lvs, dp_y_max_lvs, dp_y_view_lvs, dp_filename_suffix_lvs, path_dwnlds_lvs, path_csv_dmp_lvs)

#merge_csvs_multi_sector(xlsx_file_name_lvs2021, path_csv_dmp_lvs, dp_filename_suffix_lvs, y_focus_lvs )
#shutil.move(f'{path_csv_dmp_lvs}', f'{path_csv_dmp_lvs}_Africa_{y_focus_lvs2021}')





# Focus 2020
dp_y_min_lvs2020 =  ['2020', '2020']
dp_y_max_lvs2020 =  ['2021', '2021']
dp_y_view_lvs2020 = ['2020', '2020']
xlsx_file_name_lvs2020 = '0_dportal_LVS_health_Africa_2020'
y_focus_lvs2020 = '2020'
"""
dportal_scraper(dp_cntry_lvs, dp_sect_full_lvs, dp_stat_lvs, dp_y_min_lvs2020, dp_y_max_lvs2020, dp_y_view_lvs2020, dp_filename_suffix_lvs, path_dwnlds_lvs, path_csv_dmp_lvs)
merge_csvs_multi_sector(xlsx_file_name_lvs2020, path_csv_dmp_lvs, dp_filename_suffix_lvs, y_focus_lvs2020 )
shutil.move(f'{path_csv_dmp_lvs}', f'{path_csv_dmp_lvs}_LVS_health_Africa_{y_focus_lvs2020}')
"""




# Focus 2019
dp_y_min_lvs2019 =  ['2019', '2019']
dp_y_max_lvs2019 =  ['2020', '2020']
dp_y_view_lvs2019 = ['2019', '2019']
xlsx_file_name_lvs2019 = '0_dportal_LVS_health_Africa_2019'
y_focus_lvs2019 = '2019'
"""
dportal_scraper(dp_cntry_lvs, dp_sect_full_lvs, dp_stat_lvs, dp_y_min_lvs2019, dp_y_max_lvs2019, dp_y_view_lvs2019, dp_filename_suffix_lvs, path_dwnlds_lvs, path_csv_dmp_lvs)
merge_csvs_multi_sector(xlsx_file_name_lvs2019, path_csv_dmp_lvs, dp_filename_suffix_lvs, y_focus_lvs2019 )
shutil.move(f'{path_csv_dmp_lvs}', f'{path_csv_dmp_lvs}_LVS_health_Africa_{y_focus_lvs2019}')
"""



# only NCD for 2021
dp_sect_full_lvs_ncd = ['', '&sector_group=123']
dp_filename_suffix_lvs_ncd = ['all',  'ncd']
dp_y_min_lvs2021_ncd =  ['2021', '2021']
dp_y_max_lvs2021_ncd =  ['2022', '2022']
dp_y_view_lvs2021_ncd = ['2021', '2021']
xlsx_file_name_lvs2021_ncd = '0_dportal_LVS_ncd_Africa_2021'
y_focus_lvs2021_ncd = '2021'
"""
dportal_scraper(dp_cntry_lvs, dp_sect_full_lvs_ncd, dp_stat_lvs, dp_y_min_lvs2021_ncd, dp_y_max_lvs2021_ncd, dp_y_view_lvs2021_ncd, dp_filename_suffix_lvs_ncd, path_dwnlds_lvs, path_csv_dmp_lvs)
merge_csvs_multi_sector(xlsx_file_name_lvs2021_ncd, path_csv_dmp_lvs, dp_filename_suffix_lvs_ncd, y_focus_lvs2021_ncd )
shutil.move(f'{path_csv_dmp_lvs}', f'{path_csv_dmp_lvs}_LVS_ncd_Africa_{y_focus_lvs2021_ncd}')
"""



# only NCD for 2019
dp_y_min_lvs2019_ncd =  ['2019', '2019']
dp_y_max_lvs2019_ncd =  ['2020', '2020']
dp_y_view_lvs2019_ncd = ['2019', '2019']
xlsx_file_name_lvs2019_ncd = '0_dportal_LVS_ncd_Africa_2019'
y_focus_lvs2019_ncd = '2019'
"""
dportal_scraper(dp_cntry_lvs, dp_sect_full_lvs_ncd, dp_stat_lvs, dp_y_min_lvs2019_ncd, dp_y_max_lvs2019_ncd, dp_y_view_lvs2019_ncd, dp_filename_suffix_lvs_ncd, path_dwnlds_lvs, path_csv_dmp_lvs)
merge_csvs_multi_sector(xlsx_file_name_lvs2019_ncd, path_csv_dmp_lvs, dp_filename_suffix_lvs_ncd, y_focus_lvs2019_ncd )
shutil.move(f'{path_csv_dmp_lvs}', f'{path_csv_dmp_lvs}_LVS_ncd_Africa_{y_focus_lvs2019_ncd}')
"""



# Focus Latam 2021
cntry_LATAM_selection = ['AR', 'BB', 'CL', 'CO', 'EC', 'MX', 'PE', 'UY', 'BZ', 'BO', 'CR', 'CU', 'DO', 'SV', 'GT', 'HT', 'HN', 'JM', 'NI', 'PA', 'PY', 'PR', 'TT', 'VE', 'GY']
dp_cntry_lvs_latam = cntry_LATAM_selection

dp_y_min_lvs2021_latam =  ['2021', '2021']
dp_y_max_lvs2021_latam =  ['2022', '2022']
dp_y_view_lvs2021_latam = ['2021', '2021']
xlsx_file_name_lvs2021_latam = '0_dportal_LVS_health_LATAM_2021'
y_focus_lvs2021_latam = '2021'
"""
dportal_scraper(cntry_LATAM_selection, dp_sect_full_lvs, dp_stat_lvs, dp_y_min_lvs2021_latam, dp_y_max_lvs2021_latam, dp_y_view_lvs2021_latam, dp_filename_suffix_lvs, path_dwnlds_lvs, path_csv_dmp_lvs)
merge_csvs_multi_sector(xlsx_file_name_lvs2021_latam, path_csv_dmp_lvs, dp_filename_suffix_lvs, y_focus_lvs2021_latam )
shutil.move(f'{path_csv_dmp_lvs}', f'{path_csv_dmp_lvs}_LVS_health_LATAM_{y_focus_lvs2021_latam}')
"""



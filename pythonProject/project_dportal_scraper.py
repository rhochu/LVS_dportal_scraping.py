import numpy as np
exec(open('C:/Users/hochulir/PycharmProjects/pythonProject/project_dportal_settings.py').read())

read_files = glob.glob(f'{path_csv_dmp}/*.csv') # ATTENTION: Last two digits must be set in such a way that it gives a iso2 country code.
read_countries = []
for i in read_files:
    #print(i)
    read_countries.append(i[101:103])
np.unique(read_countries)

dp_cntry = cntry_Africa_ALL[7+9+6+3+2+3+11:99] # continue with CM
dp_cntry




# WEB SCRAPING
timer_start = datetime.datetime.now()
i_cntry = dp_cntry[0]
counter = 0
for i_cntry in dp_cntry:
    i_sttngs = 0
    for i_sttngs in range(0, len(dp_sect_full)):

        if os.path.isfile(f'{path_dwnlds}/dportal_donor_activities.csv'):
            os.remove(f'{path_dwnlds}/dportal_donor_activities.csv')
            print(f'old <<dportal_projects>> file deleted')
        else:
            print(f'no old <<dportal_projects>> file found')

        if not os.path.exists(f'{path_csv_dmp}'):
            os.mkdir(f'{path_csv_dmp}')
            print(f'dir <<scaper_dump>> created')
        else:
            print(f'dir <<scaper_dump>> exists already')

        with open(f'{path_csv_dmp}/0_timestamp.txt', 'w') as f:
            f.write('\n')
            f.write(f'{xlsx_file_name} run')
            f.write(f'run at: {datetime.date}, {datetime.datetime.now()}')
            f.write('\n')


        scrape_URL = f'https://d-portal.org/ctrack.html?country_code={i_cntry}{dp_sect_full[i_sttngs]}&status_code={dp_stat[i_sttngs]}&year_min={dp_y_min[i_sttngs]}&year_max={dp_y_max[i_sttngs]}#view=donors&year={dp_y_view[i_sttngs]}'
        print(scrape_URL)
        s = Service('C:/Users/hochulir/PycharmProjects/pythonProject/chromedriver.exe')  # go here to find matching chrome driver https://sites.google.com/chromium.org/driver/
        driver = webdriver.Chrome(service = s)
        driver.get(scrape_URL)
        time.sleep(1.5)

        # get list of all donor elements to loop through
        money_third = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,'money')))
        rows_table_for_loop = money_third.find_elements(By.CLASS_NAME, 'rows')
        #donor_name_table_for_loop = rows_table[0].find_element(By.CLASS_NAME,  'col2')
        driver.quit()
        donor_titles = []


        i_rows = 2
        for i_rows in range(0,len(rows_table_for_loop)):
            driver = webdriver.Chrome(service=s)
            driver.get(scrape_URL)
            time.sleep(2.5)
            money_fourth = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'money')))
            rows_table = money_fourth.find_elements(By.CLASS_NAME, 'rows')
            rows_table_for_ii = rows_table[i_rows]
            donor_name_table = rows_table_for_ii.find_element(By.CLASS_NAME,  'col2')
            time.sleep(1)
            donor_name_table.click()

            time.sleep(1.5)
            donor_str = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'donors_head_title'))).text[32:99]
            donor_titles += [donor_str]


            # click download button
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 
                'download_wrap'))).click()
            except TimeoutException:
                print("Loading took too much time!")
                # driver.quit()

            # set page back and sleep period to fully download csv
            time.sleep(1)
            driver.quit()

            # move csv to scraper_dump
            shutil.move(
                f'{path_dwnlds}/dportal_donor_activities.csv',
                f'{path_csv_dmp}/dportal_donor_activities_{i_cntry}_{dp_filename_suffix[i_sttngs]}_{i_rows}.csv')
            #shutil.move(f'{path_dwnlds}/dportal_donors_{i_cntry}.csv',f'{path_csv_dmp}/{i_cntry}_{dp_filename_suffix[i_sttngs]}_{dp_y_view[i_sttngs]}.csv' )

            loadingbarTO40 = round((i_rows/len(rows_table_for_loop))*40)
            print(f'{i_cntry}, country {dp_cntry.index(i_cntry)+1} of {len(dp_cntry)}: '
                  f'|{("="*loadingbarTO40)+"|"+("."*(40-loadingbarTO40))}|'
                  f' > project {i_rows+1} of {len(rows_table_for_loop)} completed')

timer_end = datetime.datetime.now()
timer_total = timer_end - timer_start

with open(f'{path_csv_dmp}/0_timestamp.txt', 'a') as f:
    f.write(f'total runtime: {timer_total} (h:mm:ss:sss)')
    f.write('\n')
    f.write('\n')
    f.write('DONOR ORGANIZATIONS INCLUDED:')
    f.write('\n')
    for line in donor_titles:
        f.write(f'> {line}')
        f.write('\n')



# FILE MERGING
timer_start = datetime.datetime.now()

if not os.path.exists(f'{path_csv_dmp}'):
    print(f'Run scraper first! No csvs to merge')
else:
    """    
    writer = pd.ExcelWriter(f'{path_csv_dmp}/{xlsx_file_name}_by_country.xlsx', engine='xlsxwriter')
    df_bycntry_conc = pd.DataFrame()
    i_cntry_name = dp_cntry[0]
    for i_cntry_name in dp_cntry:
        csv_names_dmp_bycntry = glob.glob(f'{path_csv_dmp}/*_{i_cntry_name}_*.csv')
        i_csv_name_bycntry = csv_names_dmp_bycntry[0]
        for i_csv_name_bycntry in csv_names_dmp_bycntry:
            isoname_in_filename = i_csv_name_bycntry[nameplace_in_str[0]:  nameplace_in_str[1]]
            sectorname_in_filename = i_csv_name_bycntry[sectorplace_in_str[0]:sectorplace_in_str[1]]

            df_csv = pd.read_csv(i_csv_name_bycntry, thousands=',')
            # full name, iso and sector name are added additionally to each row
            df_csv.insert(0, f'sector_selection', f'"{sectorname_in_filename}"')
            df_csv.insert(0, f'country_iso2', f'{isoname_in_filename}')
            i_csv_fullname = list(df_cntry_iso['name'][df_cntry_iso['alpha-2'] == isoname_in_filename])[0]
            df_csv.insert(0, f'country_name', f'{i_csv_fullname}')

            df_bycntry_conc = pd.concat([df_bycntry_conc, df_csv])
            del df_csv

    df_bycntry_conc.to_excel(writer, sheet_name=f'{isoname_in_filename}', index=False)
    del df_bycntry_conc
    print(f'write: {isoname_in_filename}_{sectorname_in_filename} > to XLSX by country')
    writer.save()
    time.sleep(1)
    writer.close()
    """

    writer = pd.ExcelWriter(f'{path_csv_dmp}/{xlsx_file_name}_by_sector.xlsx', engine='xlsxwriter')
    df_byfunder_conc = pd.DataFrame()
    i_sector_name = dp_filename_suffix[0]
    for i_sector_name in dp_filename_suffix:
        csv_name_dmp_bysec = glob.glob(f'{path_csv_dmp}/*_{i_sector_name}_*.csv')
        i_csv_name_bysec = csv_name_dmp_bysec[0]
        for i_csv_name_bysec in csv_name_dmp_bysec:
            isoname_in_filename =    i_csv_name_bysec[nameplace_in_str[0]:  nameplace_in_str[1]]
            sectorname_in_filename = i_csv_name_bysec[sectorplace_in_str[0]:sectorplace_in_str[1]]
            number_in_filename =     i_csv_name_bysec[number_in_str[0]:number_in_str[1]]

            region_from_filename =    df_cntry_iso['region'][df_cntry_iso['alpha-2'] == isoname_in_filename].iat[0]
            subregion_from_filename = df_cntry_iso['sub-region'][df_cntry_iso['alpha-2'] == isoname_in_filename].iat[0]

            df_csv = pd.read_csv(i_csv_name_bysec, thousands=',')
            # full name, iso and sector name are added additionally to each row
            df_csv.insert(0, f'subregion', f'{subregion_from_filename}')
            df_csv.insert(0, f'region', f'{region_from_filename}')
            df_csv.insert(0, f'sector_selection_code', f'{dp_stat}')
            df_csv.insert(0, f'sector_selection', f'"{sectorname_in_filename}"')
            df_csv.insert(0, f'year_focus', f'{dp_y_view[0]}')
            df_csv.insert(0, f'country_iso2', f'{isoname_in_filename}')
            i_csv_fullname = list(df_cntry_iso['name'][df_cntry_iso['alpha-2'] == isoname_in_filename])[0]
            df_csv.insert(0, f'country_name', f'{i_csv_fullname}')

            df_byfunder = df_csv.sort_values(by = f'total-commitment', ascending= False)
            df_byfunder_conc = pd.concat([df_byfunder_conc, df_byfunder])
            del df_csv, df_byfunder
            print(f'write: {isoname_in_filename}_{sectorname_in_filename}_{number_in_filename} > to XLSX by sector')

    df_byfunder_conc.to_excel(writer, sheet_name=f'{i_sector_name}', index=False)
    del df_byfunder_conc
    writer.save()
    time.sleep(1)
    writer.close()
    print('> file merge finished successfully')

timer_end = datetime.datetime.now()
timer_total = timer_end - timer_start

#shutil.move(f'{path_csv_dmp}', f'{path_csv_dmp}_{dp_cntry[0]}')
print(f'xlsx MERGE finished successfully \n {timer_total} h:mm:ss runtime')




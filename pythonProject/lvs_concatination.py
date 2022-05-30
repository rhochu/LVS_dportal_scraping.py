import numpy as np
import datetime
import os as os
import pandas as pd
import shutil, pathlib, time, glob
import xlsxwriter
import datetime
import tabulate

from tabulate import tabulate


path_files = f'G:/My Drive/1_LandscapingValueStreams Africa/data'
y_focus = '2021'

# create MAIN data frame
df_cntry_iso = pd.read_json('https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.json')
df_cntry_iso.columns
d = {'country_name': df_cntry_iso['name'][df_cntry_iso['region'] == 'Africa'],
     'iso2': df_cntry_iso['alpha-2'][df_cntry_iso['region'] == 'Africa'],
     'iso3': df_cntry_iso['alpha-3'][df_cntry_iso['region'] == 'Africa']}
df_MAIN = pd.DataFrame.from_dict(d).reset_index().drop(["index"], axis=1)

# added columns
df_MAIN[f'dportal_all_USD'] = np.nan
df_MAIN[f'dportal_all_names'] = np.nan
df_MAIN[f'dportal_health_USD'] = np.nan
df_MAIN[f'dportal_health_names'] = np.nan
df_MAIN[f'china_constr_USD'] = np.nan
df_MAIN[f'china_invstm_USD'] = np.nan
df_MAIN[f'remittance_USD'] = np.nan


# load relevant data frames for aggregation
df_dp_all = pd.read_excel(f'{path_files}/0_dportal_LVS_MERGED.xlsx', sheet_name='all')
df_dp_health = pd.read_excel(f'{path_files}/0_dportal_LVS_MERGED.xlsx', sheet_name='health')
df_chinv = pd.read_excel(f'{path_files}/China-Global-Investment-Tracker-2021-Fall-FINAL-2022.2.21-update.xlsx', skiprows = range(0,5), sheet_name= 'Dataset 1', )
df_chcon = pd.read_excel(f'{path_files}/China-Global-Investment-Tracker-2021-Fall-FINAL-2022.2.21-update.xlsx', skiprows = range(0,5), sheet_name= 'Dataset 2', )
df_r  = pd.read_excel(f'{path_files}/remittance_global_2017-2020.xlsx')



df_dp_all.dtypes
df_dp_health.dtypes
df_chinv.dtypes
df_chcon.dtypes
df_r.dtypes


for i in range(0,df_MAIN.shape[0]):
     print(df_MAIN['country_name'][i])
     i_cntry_iso = df_MAIN['iso2'][i]

     # all dportal donors
     sub_dp = df_dp_all[df_dp_all['country_iso2'] == i_cntry_iso].sort_values(by = f't{y_focus}', ascending= False)
     donor_list = [f'{donor_name} (USD {donor_amount})' for donor_name, donor_amount in zip(sub_dp.donor, sub_dp.t2021)]
     donor_string = '; '.join(donor_list[:10])
     df_MAIN.loc[i, (f'dportal_all_names')] = donor_string
     df_MAIN.loc[i, (f'dportal_all_USD')] = df_dp_all[f't{y_focus}'][df_dp_all['country_iso2'] == i_cntry_iso].sum()
     del sub_dp, donor_list, donor_string

     # health dportal donors
     sub_dp = df_dp_health[df_dp_health['country_iso2'] == i_cntry_iso].sort_values(by = f't{y_focus}', ascending= False)
     donor_list = [f'{donor_name} (USD {donor_amount})' for donor_name, donor_amount in zip(sub_dp.donor, sub_dp.t2021)]
     donor_string = '; '.join(donor_list[:10])
     df_MAIN.loc[i, (f'dportal_health_names')] = donor_string
     df_MAIN.loc[i, (f'dportal_health_USD')] = df_dp_all[f't{y_focus}'][df_dp_all['country_iso2'] == i_cntry_iso].sum()
     del sub_dp, donor_list, donor_string

     # health construction China

     # health investment China

     # remittance






df_MAIN.head()
df_dp_all.head()
df_MAIN.columns

i = 0
i_cntry_iso = df_MAIN['iso2'][i]



df_dp_all.dtypes
df_dp_health.dtypes
df_chinv.dtypes
df_chcon.dtypes
df_r.dtypes

print(tabulate(df_dp_all, headers='keys', tablefmt='psql'))
print(tabulate(df_chinv, headers='keys', tablefmt='psql'))
print(tabulate(d, headers='keys', tablefmt='psql'))
print(tabulate(df_MAIN, headers='keys', tablefmt='psql'))
print(tabulate(x, headers='keys', tablefmt='psql'))
type(df_MAIN)
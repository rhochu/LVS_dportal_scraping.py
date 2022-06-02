import numpy as np
import datetime
import os as os
import pandas as pd
import shutil, pathlib, time, glob
import xlsxwriter
import datetime
import tabulate

from tabulate import tabulate

# parameter setup
path_files = f'G:/My Drive/1_LandscapingValueStreams Africa/data'
y_focus = '2021'

# create MAIN data frame
df_cntry_iso = pd.read_json('https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.json')
df_cntry_iso.columns
d = {'country_name': df_cntry_iso['name'][df_cntry_iso['region'] == 'Africa'],
     'iso2': df_cntry_iso['alpha-2'][df_cntry_iso['region'] == 'Africa'],
     'iso3': df_cntry_iso['alpha-3'][df_cntry_iso['region'] == 'Africa']}
df_MAIN = pd.DataFrame.from_dict(d).reset_index().drop(["index"], axis=1)


# load relevant data frames for aggregation and change value classes
df_dp_all = pd.read_excel(f'{path_files}/0_dportal_LVS_MERGED.xlsx', sheet_name='all')
df_dp_health = pd.read_excel(f'{path_files}/0_dportal_LVS_MERGED.xlsx', sheet_name='health')
df_chinv = pd.read_excel(f'{path_files}/China-Global-Investment-Tracker-2021-Fall-FINAL-2022.2.21-update.xlsx', skiprows = range(0,5), sheet_name= 'Dataset 1', )
df_chcon = pd.read_excel(f'{path_files}/China-Global-Investment-Tracker-2021-Fall-FINAL-2022.2.21-update.xlsx', skiprows = range(0,5), sheet_name= 'Dataset 2', )
df_wb  = pd.read_excel(f'{path_files}/Data_Extract_From_World_Development_Indicators.xlsx')


# transfer "object" class to "string"
df_dp_all[['country_name', 'country_iso2', 'd-portal name setting', 'donor', 'currency' ]] = df_dp_all[['country_name', 'country_iso2', 'd-portal name setting', 'donor', 'currency' ]].astype("string")
df_dp_all.dtypes
df_dp_health[['country_name', 'country_iso2', 'd-portal name setting', 'donor', 'currency' ]] = df_dp_health[['country_name', 'country_iso2', 'd-portal name setting', 'donor', 'currency' ]].astype("string")
df_dp_health.dtypes
df_chinv[['Year', 'Month', 'Investor', 'Share Size', 'Transaction Party', 'Sector', 'Subsector', 'Country', 'Country_iso2', 'Country_iso_full', 'Region', 'Greenfield' ]] = df_chinv[['Year', 'Month', 'Investor', 'Share Size', 'Transaction Party', 'Sector', 'Subsector', 'Country', 'Country_iso2', 'Country_iso_full', 'Region', 'Greenfield' ]].astype("string")
df_chinv.dtypes
df_chcon[['Year', 'Month', 'Contractor', 'Share Size', 'Transaction Party', 'Sector', 'Subsector', 'Country', 'Country_iso2', 'Country_iso_full', 'Region', 'BRI' ]] = df_chcon[['Year', 'Month', 'Contractor', 'Share Size', 'Transaction Party', 'Sector', 'Subsector', 'Country', 'Country_iso2', 'Country_iso_full', 'Region', 'BRI' ]].astype("string")
df_chcon.dtypes

#remove ".." from df for nan an drop last rows that are included because of "timestamp" by world bank
df_wb = df_wb.replace('..',np.nan)
df_wb.drop(df_wb.tail(5).index, inplace = True)

#shorter names for facility in WB set
old_wb_names = df_wb.columns.values.tolist()
new_wb_names = ['Country Name',
                'Country Code',
                'Time',
                'Time Code',
                'pop_tot',
                'pop_growth_perc',
                'age_dep_rat_tot',
                'age_dep_rat_old',
                'age_dep_rat_young',
                'hex_perc_gdp',
                'gov_hex_perc_gdp',
                'GDP_USD',
                'GDP_ann_growth_perc',
                'hex_pcap_USD',
                'financial_sect_rating',
                'corruption_rating',
                'gov_hex_pcap_USD',
                'gov_hex_perc_of_hex_tot',
                'private_hex_perc_of_hex_tot',
                'private_hex_pcap_USD',
                'ext_hex_pcap_USD',
                'ext_hex_perc_of_hex_tot',
                'Life_expec_tot_years',
                'oop_hex_perc_of_hex_tot',
                'oop_hex_pcap_USD',
                'physicians_p1000cap',
                'risk_of_catastrophic_expenditure_for_surgical_care_(%_of_people_at_risk)',
                'risk_of_impoverishing_expenditure_for_surgical_care_(%_of_people_at_risk)',
                'hosp_beds_p1000cap',
                'pers_remittances_received_perc_gdp',
                'pers_remittances_received_USD']

new_wb_names[20:24]
old_wb_names[20:24]

df_wb.columns = new_wb_names

add_wb_variables = new_wb_names.copy()
# bring remittance to the front of the variable set
#add_wb_variables.remove('pers_remittances_received_USD')
add_wb_variables.remove('Country Name')
add_wb_variables.remove('Country Code')
add_wb_variables.remove('Time')
add_wb_variables.remove('Time Code')

len(new_wb_names)
len(add_wb_variables)




# add new empty columns to MAIN that are required later


new_colnames_dp = ['dportal_all_USD', 'dportal_all_names', 'dportal_health_USD', 'dportal_health_names']
new_colnames_ch = ['china_invstm_all_USD', 'china_invstm_all_names', 'china_invstm_health_USD', 'china_invstm_health_names',
                   'china_constr_all_USD','china_constr_all_names', 'china_constr_health_USD', 'china_constr_health_names']

s1 = pd.Series(add_wb_variables)[['pers_remittances_received_USD' in  x for x in add_wb_variables]]
s2 = pd.Series(add_wb_variables)[ np.invert(['pers_remittances_received_USD' in  x for x in add_wb_variables])]
add_wb_variables = pd.concat([s1,s2])


df_MAIN = pd.concat([df_MAIN,pd.DataFrame(columns= ['roche_affiliate'])])
df_MAIN = pd.concat([df_MAIN,pd.DataFrame(columns= new_colnames_dp)])
df_MAIN = pd.concat([df_MAIN,pd.DataFrame(columns= new_colnames_ch)])
df_MAIN = pd.concat([df_MAIN,pd.DataFrame(columns= add_wb_variables)])

df_MAIN.columns



# merge functions

i = 41
print(df_MAIN['country_name'][i], df_MAIN['iso2'][i])
i_cntry_iso = df_MAIN['iso2'][i]
i_cntry_iso3 = df_MAIN['iso3'][i]

# fun_df_dp = df_dp_all
# fun_MAIN_colname = 'dportal_all'
def dportal_to_MAIN(fun_df_dp, fun_MAIN_colname):
    sub_dp = fun_df_dp[fun_df_dp['country_iso2'] == i_cntry_iso].sort_values(by=f't{y_focus}', ascending=False)
    MAIN_col_name = fun_MAIN_colname

    donor_list = [f'{donor_name} (USD {donor_amount})' for donor_name, donor_amount in
                  zip(sub_dp['donor'], sub_dp[f't{y_focus}'])]
    donor_string = '; '.join(donor_list[:10])
    df_MAIN.loc[i, (f'{MAIN_col_name}_names')] = donor_string
    df_MAIN.loc[i, (f'{MAIN_col_name}_USD')] = sub_dp[f't{y_focus}'].sum()
    df_MAIN.loc[i, (f'{MAIN_col_name}_names')]
    df_MAIN.loc[i, (f'{MAIN_col_name}_USD')]


# fun_df_ch = df_chinv
# fun_health_TF = False
# fun_ch_col_name = 'Investor'
# fun_MAIN_colname = 'china_invstm_all'
def china_invstm_to_MAIN(fun_df_ch, fun_health_TF, fun_MAIN_colname):
    if fun_health_TF:
        sub_ch = fun_df_ch[(fun_df_ch['Country_iso2'] == i_cntry_iso) & (fun_df_ch['Year'] == f'{y_focus}') & (
                    fun_df_ch['Sector'] == 'Health')].sort_values(by=f'Quantity in Millions', ascending=False)
    elif not fun_health_TF:
        sub_ch = fun_df_ch[
            (fun_df_ch['Country_iso2'] == i_cntry_iso) & (fun_df_ch['Year'] == f'{y_focus}')].sort_values(
            by=f'Quantity in Millions', ascending=False)

    if 'Investor' in fun_df_ch.columns.values.tolist():
        ch_col_name = 'Investor'
    elif 'Contractor' in fun_df_ch.columns.values.tolist():
        ch_col_name = 'Contractor'

    MAIN_col_name = fun_MAIN_colname

    donor_list = [f'{donor_name} (USD {donor_amount})' for donor_name, donor_amount in
                  zip(sub_ch[f'{ch_col_name}'], sub_ch['Quantity in Millions'])]
    donor_string = '; '.join(donor_list[:10])
    df_MAIN.loc[i, (f'{MAIN_col_name}_names')] = donor_string
    df_MAIN.loc[i, (f'{MAIN_col_name}_USD')] = sub_ch['Quantity in Millions'].sum() * 1000000
    df_MAIN.loc[i, (f'{MAIN_col_name}_names')]
    df_MAIN.loc[i, (f'{MAIN_col_name}_USD')]



# transfer data from all sources to MAIN
for i in range(0,df_MAIN.shape[0]):
    i_cntry_iso = df_MAIN['iso2'][i]
    i_cntry_iso3 = df_MAIN['iso3'][i]

    dportal_to_MAIN(df_dp_all, 'dportal_all')
    dportal_to_MAIN(df_dp_health, 'dportal_health')

    china_invstm_to_MAIN(df_chinv, False, 'china_invstm_all')
    china_invstm_to_MAIN(df_chinv, True,  'china_invstm_health')
    china_invstm_to_MAIN(df_chcon, False, 'china_constr_all')
    china_invstm_to_MAIN(df_chcon, True,  'china_constr_health')


    #remaining Development Indicators from WB
    y_focus_minus1 = str(pd.to_numeric(y_focus, errors='coerce') - 1)
    y_focus_minus2 = str(pd.to_numeric(y_focus, errors='coerce') - 2)

    for ii in add_wb_variables:
        check_year_minus1 = df_wb[f'{ii}'][(df_wb['Country Code'] == 'WLD') & (df_wb['Time Code'] == f'YR{y_focus_minus1}')].values.item()
        check_year_minus2 = df_wb[f'{ii}'][(df_wb['Country Code'] == 'WLD') & (df_wb['Time Code'] == f'YR{y_focus_minus2}')].values.item()

        if not pd.isnull(check_year_minus1):
            y_focus_ii = y_focus_minus1
        elif not pd.isnull(check_year_minus2):
            y_focus_ii = y_focus_minus2

        df_MAIN.loc[i, (f'{ii}')] = df_wb[f'{ii}'][(df_wb['Country Code'] == i_cntry_iso3) & (df_wb['Time Code'] == f'YR{y_focus_ii}')].sum()

    print(f'loop finished for "{df_MAIN["country_name"][i]} ({df_MAIN["iso2"][i]})"')


#add year at end of column header
y_focus_minus1 = str(pd.to_numeric(y_focus, errors='coerce') - 1)
y_focus_minus2 = str(pd.to_numeric(y_focus, errors='coerce') - 2)

for ii in add_wb_variables:
    check_year_minus1 = df_wb[f'{ii}'][(df_wb['Country Code'] == 'WLD') & (df_wb['Time Code'] == f'YR{y_focus_minus1}')].values.item()
    check_year_minus2 = df_wb[f'{ii}'][(df_wb['Country Code'] == 'WLD') & (df_wb['Time Code'] == f'YR{y_focus_minus2}')].values.item()

    if not pd.isnull(check_year_minus1):
        y_focus_ii = y_focus_minus1
    elif not pd.isnull(check_year_minus2):
        y_focus_ii = y_focus_minus2
    df_MAIN.rename(columns={f'{ii}': f'{ii}_{y_focus_ii}'}, inplace = True)



# add roche affiliate indicator
['Algeria','Congo, Democratic Republic of the','Côte d\'Ivoire','Ethiopia','Ghana','Kenya','Liberia','Libya','Morocco','Nigeria','South Africa','Tunisia']
roche_aff = ['DZ','CD','CI','ET','GH','KE','LR','LY','MA','NG','ZA','TN']
df_MAIN['roche_affiliate'][df_MAIN['iso2'].isin(roche_aff)] = 1
df_MAIN['roche_affiliate'][np.invert(df_MAIN['iso2'].isin(roche_aff))] = 0
df_MAIN['roche_affiliate']




# excel export
writer = pd.ExcelWriter(f'{path_files}/all_sources_CONCAT_to_MAIN.xlsx', engine='xlsxwriter')
df_MAIN.to_excel(writer, sheet_name= 'concatinated_data', index=False)
writer.save()
time.sleep(1)
writer.close()



#print(tabulate(df_dp_all, headers='keys', tablefmt='psql'))
#print(tabulate(df_chinv, headers='keys', tablefmt='psql'))
#print(tabulate(df_MAIN, headers='keys', tablefmt='psql'))

print(f'>>> finished concatenated, woop woop :))')



import main

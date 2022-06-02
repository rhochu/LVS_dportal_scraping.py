

print(tabulate(df, headers='keys', tablefmt='psql'))

path_csv_dmp = path_csv_dmp_lvs
dp_filename_suffix = dp_filename_suffix_lvs
i_csv_name = 'C:/Users/hochulir/Desktop/scraper_csv_dump\\VN_current.csv'
xlsx_file_name = '0_dportal_LVS'



xlsx_file_name = 'asdf'

dp_filename_suffix = dp_filename_suffix_lvs
i_sector_name = dp_filename_suffix[0]

i_sector_name
csv_name_dmp_bysec = glob.glob(f'{path_csv_dmp}/*_{i_sector_name}.csv')
csv_name_dmp_bysec
i_csv_name_bysec = csv_name_dmp_bysec[0]

i_csv_name_bysec

i_csv_name_bysec[67:69]




dp_cntry = dp_cntry_lvs
i_sector_name
csv_name_dmp_bysec = glob.glob(f'{path_csv_dmp}/*_{i_sector_name}.csv')
i_csv_name_bysec = csv_name_dmp_bysec[0]
i_csv_name_bysec
i_csv_name_bysec = csv_name_dmp_bysec[1]
i_csv_name_bysec










# ============================================================================
# =======  DATA TRANSFER FROM CHINA INVESTMENT TRACKER TO MAIN ===============
# ============================================================================


# all construction China
sub_ch = df_chcon[(df_chcon['Country_iso2'] == i_cntry_iso) & (df_chcon['Year'] == f'{y_focus}')].sort_values(
     by=f'Quantity in Millions', ascending=False)
ch_col_name = 'Contractor'
MAIN_col_name = 'china_constr_all'
sub_ch
donor_list = [f'{donor_name} (USD {donor_amount})' for donor_name, donor_amount in
              zip(sub_ch[f'{ch_col_name}'], sub_ch['Quantity in Millions'])]
donor_string = '; '.join(donor_list[:10])
df_MAIN.loc[i, (f'{MAIN_col_name}_names')] = donor_string
df_MAIN.loc[i, (f'{MAIN_col_name}_mn_USD')] = sub_ch['Quantity in Millions'].sum()
df_MAIN.loc[i, (f'{MAIN_col_name}_names')]
df_MAIN.loc[i, (f'{MAIN_col_name}_mn_USD')]
del sub_ch, ch_col_name, MAIN_col_name, donor_list, donor_string

# health construction China
sub_ch = df_chcon[(df_chcon['Country_iso2'] == i_cntry_iso) & (df_chcon['Year'] == f'{y_focus}') & (
             df_chcon['Sector'] == 'Health')].sort_values(by=f'Quantity in Millions', ascending=False)
ch_col_name = 'Contractor'
MAIN_col_name = 'china_constr_health'
sub_ch
donor_list = [f'{donor_name} (USD {donor_amount})' for donor_name, donor_amount in
              zip(sub_ch[f'{ch_col_name}'], sub_ch['Quantity in Millions'])]
donor_string = '; '.join(donor_list[:10])
df_MAIN.loc[i, (f'{MAIN_col_name}_names')] = donor_string
df_MAIN.loc[i, (f'{MAIN_col_name}_mn_USD')] = sub_ch['Quantity in Millions'].sum()
df_MAIN.loc[i, (f'{MAIN_col_name}_names')]
df_MAIN.loc[i, (f'{MAIN_col_name}_mn_USD')]
del sub_ch, ch_col_name, donor_list, donor_string

# all investment China
sub_ch = df_chinv[(df_chinv['Country_iso2'] == i_cntry_iso) & (df_chinv['Year'] == f'{y_focus}')].sort_values(
     by=f'Quantity in Millions', ascending=False)
ch_col_name = 'Investor'
MAIN_col_name = 'china_invstm_all'
sub_ch
donor_list = [f'{donor_name} (USD {donor_amount})' for donor_name, donor_amount in
              zip(sub_ch[f'{ch_col_name}'], sub_ch['Quantity in Millions'])]
donor_string = '; '.join(donor_list[:10])
df_MAIN.loc[i, (f'{MAIN_col_name}_names')] = donor_string
df_MAIN.loc[i, (f'{MAIN_col_name}_mn_USD')] = sub_ch['Quantity in Millions'].sum()
df_MAIN.loc[i, (f'{MAIN_col_name}_names')]
df_MAIN.loc[i, (f'{MAIN_col_name}_mn_USD')]
del sub_ch, ch_col_name, donor_list, donor_string

# health investment China
sub_ch = df_chinv[(df_chinv['Country_iso2'] == i_cntry_iso) & (df_chinv['Year'] == f'{y_focus}') & (
             df_chinv['Sector'] == 'Health')].sort_values(by=f'Quantity in Millions', ascending=False)
ch_col_name = 'Investor'
MAIN_col_name = 'china_invstm_health'
sub_ch
donor_list = [f'{donor_name} (USD {donor_amount})' for donor_name, donor_amount in
              zip(sub_ch[f'{ch_col_name}'], sub_ch['Quantity in Millions'])]
donor_string = '; '.join(donor_list[:10])
df_MAIN.loc[i, (f'{MAIN_col_name}_names')] = donor_string
df_MAIN.loc[i, (f'{MAIN_col_name}_mn_USD')] = sub_ch['Quantity in Millions'].sum()
df_MAIN.loc[i, (f'{MAIN_col_name}_names')]
df_MAIN.loc[i, (f'{MAIN_col_name}_mn_USD')]
del sub_ch, ch_col_name, donor_list, donor_string





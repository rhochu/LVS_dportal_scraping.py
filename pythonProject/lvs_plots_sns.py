import numpy as np
import os as os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import pathlib, time, glob, datetime, tabulate, xlsxwriter, expression, plotnine

from tabulate import tabulate
from plotnine import *
from plotnine import ggplot, aes, geom_point


path_data_files = f'G:/My Drive/1_LandscapingValueStreams Africa/data'
path_plots = f'G:/My Drive/1_LandscapingValueStreams Africa/data/plots'


# PREWORK
df_MAIN = pd.read_excel(f'{path_data_files}/all_sources_CONCAT_to_MAIN.xlsx', index_col= None)
df_MAIN.dtypes

# variables to compare to...
non_lvs_colnames = df_MAIN.columns.tolist()[17:99]
lvsUSD_colnames = ['dportal_all_USD', 'dportal_health_USD', 'china_invstm_all_USD', 'china_invstm_health_USD', 'china_constr_all_USD', 'china_constr_health_USD']


# transform to LONG df
df_MAIN_lvsUSD_long = df_MAIN.melt(id_vars = 'iso3', value_vars = lvsUSD_colnames, var_name = 'donor_type', value_name = 'USD').copy()
print(tabulate(df_MAIN_lvsUSD_long, headers='keys', tablefmt='psql'))
df_MAIN_lvsUSD_long.dtypes
df_MAIN_lvsUSD_long['USD'] = df_MAIN_lvsUSD_long['USD'].astype(float)


# transform to WIDE df
df_MAIN.columns
df_MAIN_lvsUSD_wide = df_MAIN[['country_name', 'iso2', 'iso3', 'dportal_all_USD', 'dportal_health_USD', 'china_invstm_all_USD', 'china_invstm_health_USD', 'china_constr_all_USD', 'china_constr_health_USD', 'pers_remittances_received_USD_2020', ]].copy()
df_MAIN_lvsUSD_wide.dtypes
df_MAIN_lvsUSD_wide['pers_remittances_received_USD_2020'] = df_MAIN_lvsUSD_wide['pers_remittances_received_USD_2020'].astype(np.int64)



df_MAIN.dtypes
df_plot = df_MAIN.copy()
#df_plot_14.loc[:,lvsUSD_colnames] = df_plot_14.loc[:,lvsUSD_colnames].div(df_plot_14.loc[:,['pop_tot_2020']].iloc[:,0], axis = 0)


# df_plot = df_MAIN
fields = ['dportal_all_USD', 'china_invstm_all_USD', 'china_constr_all_USD' ]#, 'pers_remittances_received_USD_2020']
#fields = ['dportal_health_USD', 'china_invstm_health_USD', 'china_health_all_USD']
colors = ['#404FDE', '#D16676', '#2EBF4B' ]#, '#EDE43B']
labels = ['dportal all', 'china inv', 'china constr']#, 'global remittance']
cntry_column = 'iso3'
plot_title = 'TITLE test / per capita!'
export_TF = True
row_sum_value_TF = True

bar_width = 0.5
barfig_width = 15
barfig_length = 25

plt.rc('ytick', labelsize=15)
plt.rc('xtick', labelsize=15)
bar_label_size = 1



def barplot_stacked(df_plot,fields, colors, labels, cntry_column, plot_title,  export_TF):

    df_plot['row_sum'] = df_plot.loc[:, fields].sum(axis = 1)
    df_plot['row_sum'] = df_plot['row_sum'] / 1000000
    df_plot[fields] = df_plot[fields] / 1000000
    df_plot = df_plot[(df_plot['row_sum'] != np.inf) & (df_plot['row_sum'] >0) & ( np.invert( df_plot['roche_affiliate'].isna()) )] # include only greater 0 and no NaN
    df_plot_sorted = df_plot.sort_values(by = [ 'roche_affiliate_order', 'row_sum'], ascending = [False, True]).reset_index(drop = True).loc[:, (cntry_column.split()+ ['roche_affiliate', 'roche_affiliate_order', 'row_sum'] + fields)]
    # sort by row_sum of selected variables and order of Roche affiliates to form groups; keep only selected variables
    df_plot_sorted = df_plot_sorted.set_index(df_plot_sorted[f'{cntry_column}'])  # make label series to index of plot df


    fig, ax = plt.subplots(1, figsize=(barfig_width, barfig_length))

    if not row_sum_value_TF:
        bottom_bar = df_plot_sorted[f'{fields[0]}'] * [0]
        for i in range(0,len(fields)):
            # vertical bars
            # bar_container = ax.bar(df_plot_sorted[f'{cntry_column}'], df_plot_sorted[f'{fields[i]}'],  width  =  bar_width, bottom=bottom_bar, align='center', label=f'{labels[i]}', color=f'{colors[i]}')
            # horizontal bars
            bar_container = ax.barh(df_plot_sorted[f'{cntry_column}'], df_plot_sorted[f'{fields[i]}'], height =  bar_width, left = bottom_bar, align='center', label=f'{labels[i]}', color=f'{colors[i]}' )
            bottom_bar = bottom_bar + df_plot_sorted[f'{fields[i]}']



    # presettings:_title, legend, labels
    ax.legend(loc='best', fontsize=bar_label_size)


    # title
    ax.set_title(f'{plot_title}\n', loc='left')

    # x axis
    ax.set_xlabel(f'USD million')
    #for tick in ax.get_xticklabels():     # rotation of x ticks
    #    tick.set_rotation(90)

    # y axis
    #ax2 = ax.twinx()

    # legend
    plt.legend(labels, bbox_to_anchor=([1, 1.025, 0, 0]), ncol=4, frameon=True)

    # bar labels
    # ax.bar_label(bar_container, rotation = 90, padding = 30) # label_type = 'center

    # remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # adjust limits and draw grid lines
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='gray', linestyle='dotted')

    # export plot
    if export_TF:
        if not os.path.exists(f'{path_plots}'):
            os.mkdir(f'{path_plots}')
        elif os.path.exists(f'{path_plots}'):
            print('')
        # plt.show()

        plt.savefig(f'{path_plots}/{plot_title}.png')
        print('>> plot exported')

    elif not export_TF:
        print('')


df_plot = df_MAIN.copy
lvs_variables = ['dportal_all_USD', 'china_invstm_all_USD', 'china_constr_all_USD']
lvs_variables2 = ['dportal_health_USD', 'china_invstm_health_USD', 'china_constr_health_USD']
compare_variable = 'GDP_USD_2020'
labels_col = 'iso3'
plot_title = f'Development Flows into Africa compared to {compare_variable}'
export_TF = True
def bubbleplot_comparison(df_plot,lvs_variables, compare_variable, labels_col, plot_title, export_TF, *args):
    fig, ax = plt.subplots(1, figsize=(12, 10))

    df_plot['lvs_sum'] = df_plot.loc[:, lvs_variables].sum(axis = 1)
    ax.scatter(df_plot.loc[:,'lvs_sum'], df_plot.loc[:,f'{compare_variable}'])

    labels = df_MAIN.loc[:,f'{labels_col}']
    for i, txt in enumerate(labels):
        ax.annotate(txt, ( df_plot.loc[:,'lvs_sum'][i], df_plot.loc[:,f'{compare_variable}'][i]) )

    # title, legend, labels
    plt.title(f'{plot_title}\n', loc='left')
    plt.ylabel('monetary flows (USD)')
    plt.xlabel(f'{compare_variable}')

    # remove spines
    #ax.spines['right'].set_visible(False)
    #ax.spines['top'].set_visible(False)
    #ax.spines['left'].set_visible(False)
    #ax.spines['bottom'].set_visible(False)

    # adjust limits and draw grid lines
    #plt.ylim(-0.5, ax.get_yticks()[-1] + 0.5)
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='gray', linestyle='dotted')
    ax.yaxis.grid(color='gray', linestyle='dotted')

    try:
        lvs_variables2
    except NameError:
        print('no second lvs variable set')
    else:
        print('second lvs variable set exists')

        df_plot['lvs_sum2'] = df_plot.loc[:, lvs_variables2].sum(axis=1)
        ax.scatter(df_plot.loc[:, 'lvs_sum2'], df_plot.loc[:, f'{compare_variable}'], color = 'yellow' )
        labels = df_MAIN.loc[:, f'{labels_col}']
        for i, txt in enumerate(labels):
            ax.annotate(txt, (df_plot.loc[:, 'lvs_sum2'][i], df_plot.loc[:, f'{compare_variable}'][i]))


    if export_TF:
        if not os.path.exists(f'{path_plots}'):
            os.mkdir(f'{path_plots}')
        elif os.path.exists(f'{path_plots}'):
            plt.show()

        plt.savefig(f'{path_plots}/{plot_title}.png')
        print('>> plot exported')

    elif not export_TF:
        print('')




# BARPLOTS

# all projects + remittance
df_plot_1 = df_MAIN
fields_1 = ['dportal_all_USD', 'china_invstm_all_USD', 'china_constr_all_USD', 'pers_remittances_received_USD_2020']
colors_1 = ['#404FDE', '#D16676', '#2EBF4B', '#EDE43B']
labels_1 = ['dportal projects', 'china investments', 'china constructions', 'global remittance']
cntry_column_1 = 'country_name'
plot_title_1 = 'Development Flows, all sectors + remittance'
export_TF_1  = True
barplot_stacked(df_plot_1, fields_1, colors_1, labels_1, cntry_column_1 , plot_title_1, export_TF_1)

# all projects without remittance
fields_12 = ['dportal_all_USD', 'china_invstm_all_USD', 'china_constr_all_USD']
colors_12 =  ['#404FDE', '#D16676', '#2EBF4B']
labels_12 = ['dportal projects', 'china investments', 'china constructions']
plot_title_12 = 'Development Flows, all sectors'
#barplot_stacked(df_plot_1, fields_12, colors_12, labels_12, cntry_column_1 , plot_title_12, export_TF_1)

# health projects
fields_13 = ['dportal_health_USD', 'china_invstm_health_USD', 'china_constr_health_USD']
colors_13 = ['#21B4FF', '#FFA83B', '#48FF9F']
labels_13 = ['dportal', 'china investments', 'china constructions']
plot_title_13 = 'Development Flows, HEALTH sectors'
#barplot_stacked(df_plot_1, fields_13, colors_13, labels_13, cntry_column_1 , plot_title_13, export_TF_1)

# all projects projects, per capita
df_plot_14 = df_MAIN.copy() # wtih df_plot_14, all LVS components are divided by the total pop of 2020
df_plot_14.loc[:,lvsUSD_colnames] = df_plot_14.loc[:,lvsUSD_colnames].div(df_plot_14.loc[:,['pop_tot_2020']].iloc[:,0], axis = 0)
fields_14 = ['dportal_all_USD', 'china_invstm_all_USD', 'china_constr_all_USD']#, 'pers_remittances_received_USD_2020']
labels_14 =  ['dportal', 'china investments', 'china constructions'] # fields_14 #['dportal all per capita', 'china inv all per capita', 'china constr all per capita']
plot_title_14=  'Development Flows, all sectors per capita'
#barplot_stacked(df_plot_14, fields_14, colors_12, labels_14, cntry_column_1 , plot_title_14, export_TF_1)

# health projects projects, per capita
fields_15 = ['dportal_health_USD', 'china_invstm_health_USD', 'china_constr_health_USD']#, 'pers_remittances_received_USD_2020']
labels_15=  ['dportal', 'china investments', 'china constructions']  #fields_15 #['dportal health per capita', 'china inv health per capita', 'china constr health per capita']
plot_title_15= 'Development Flows, HEALTH sectors per capita'
#barplot_stacked(df_plot_14, fields_15, colors_13, labels_15, cntry_column_1 , plot_title_15, export_TF_1)






# BUBBLE PLOTS
df_plot_21 = df_MAIN
lvs_variables_21 = ['dportal_all_USD', 'china_invstm_all_USD', 'china_constr_all_USD']
compare_variable_21 = 'GDP_USD_2020'
labels_col_2 = 'iso3'
plot_title_21 = f'Development Flows into Africa compared to {compare_variable}'
export_TF_2 = True
#bubbleplot_comparison(df_plot_21,lvs_variables_21, compare_variable_21, labels_col_2, plot_title_21, export_TF_2)



# ===============================================




print(tabulate(df_MAIN, headers='keys', tablefmt='psql'))
print(tabulate(df_plot_14, headers='keys', tablefmt='psql'))


"""

url = "https://raw.githubusercontent.com/anazalea/pySankey/master/pysankey/fruits.txt"
df = pd.read_csv(url, sep=" ", names=["true", "predicted"])


print(tabulate( df, headers='keys', tablefmt='psql'))

# bar plot, https://towardsdatascience.com/stacked-bar-charts-with-pythons-matplotlib-f4020e4eb4a7



df_plot_14 = df_MAIN.copy()
df_plot_14.loc[:,lvsUSD_colnames] = df_plot_14.loc[:,lvsUSD_colnames].div(df_plot_14.loc[:,['pop_tot_2020']].iloc[:,0], axis = 0)
df_plot = df_MAIN

# df_plot = df_MAIN
fields = ['dportal_all_USD', 'china_invstm_all_USD', 'china_constr_all_USD']#, 'pers_remittances_received_USD_2020']
#fields = ['dportal_health_USD', 'china_invstm_health_USD', 'china_health_all_USD']
#colors = ['#404FDE', '#D16676', '#2EBF4B', '#EDE43B']
labels = fields
cntry_column = 'country_name'
plot_title = 'TITLE test / per capita!'
export_TF = True

def sankeyplot_ranked(df_plot,fields, colors, labels, cntry_column, plot_title,  export_TF):
    df_plot_a = df_plot.copy()
    df_plot_b = df_plot.copy()
    df_plot_b.loc[:, lvsUSD_colnames] = df_plot_b.loc[:, lvsUSD_colnames].div(df_plot_b.loc[:, ['pop_tot_2020']].iloc[:, 0], axis=0)

    df_plot_a['row_sum'] = df_plot_a.loc[:, fields].sum(axis=1)
    df_plot_b['row_sum'] = df_plot_b.loc[:, fields].sum(axis=1)

    df_plot_b = df_plot_b[(df_plot_b['row_sum'] != np.inf) & (df_plot_b['row_sum'] >0)]
    df_plot_a = df_plot_a[df_plot_a['iso3'].isin(df_plot_b['iso3'])]

    df_plot_a_sorted= df_plot_a.sort_values(by= 'row_sum', ascending= True).reset_index(drop = True)#.loc[:, (cntry_column.split() + fields)]
    df_plot_b_sorted= df_plot_b.sort_values(by= 'row_sum', ascending= True).reset_index(drop = True)#.loc[:, (cntry_column.split() + fields)]
    #df_plot_a_sorted = df_plot_a_sorted.set_index(df_plot_a_sorted[f'{cntry_column}'])
    #df_plot_b_sorted = df_plot_b_sorted.set_index(df_plot_b_sorted[f'{cntry_column}'])






# https://towardsdatascience.com/slope-charts-with-pythons-matplotlib-2c3456c137b8




"""

















"""

    from pySankey.sankey import sankey
    sankey(df_plot_a_sorted[f'{cntry_column}'], df_plot_b_sorted[f'{cntry_column}'],  aspect=20, fontsize=8)









    fig, ax = plt.subplots(1, figsize=(12, 10))
    left = len(df_plot) * [0]

    for idx, name in enumerate(fields):
    # plt.barh(df_plot_sorted.index, df_plot_sorted[f'{name}'], left = left, color=colors[idx])
        #left = left + df_plot_sorted[name]

    # title, legend, labels
    plt.title(f'{plot_title}\n', loc='left')
    plt.legend(labels, bbox_to_anchor=([1, 1.05, 0, 0]), ncol=4, frameon=False)
    plt.xlabel('USD')

    # remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # adjust limits and draw grid lines
    #plt.ylim(-0.5, ax.get_yticks()[-1] + 0.5)
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='gray', linestyle='dotted')

    if export_TF:
        if not os.path.exists(f'{path_plots}'):
            os.mkdir(f'{path_plots}')
        elif os.path.exists(f'{path_plots}'):
            plt.show()

        plt.savefig(f'{path_plots}/{plot_title}.png')
        print('>> plot exported')

    elif not export_TF:
        print('')






# =======================================

url = "https://raw.githubusercontent.com/anazalea/pySankey/master/pysankey/fruits.txt"
df = pd.read_csv(url, sep=" ", names=["true", "predicted"])


colors = {
    "apple": "#f71b1b",
    "blueberry": "#1b7ef7",
    "banana": "#f3f71b",
    "lime": "#12e23f",
    "orange": "#f78c1b"
}

sankey(df["true"], df["predicted"], aspect=20, fontsize=12)

type(df["true"])
df.dtypes
"""
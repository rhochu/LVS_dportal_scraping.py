import numpy as np
import os as os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import pathlib, time, glob, datetime, tabulate, xlsxwriter, expression, plotnine

from tabulate import tabulate
from plotnine import *
from plotnine import ggplot, aes, geom_point
from adjustText import adjust_text
from scipy import stats
from scipy.stats import pearsonr

path_data_files = f'G:/My Drive/1_LandscapingValueStreams Africa/data'
path_plots = f'G:/My Drive/1_LandscapingValueStreams Africa/data/plots'
y_focus = f'2021'
region_focus = 'Africa'
sector_focus = 'health' # besides the projects for all

df_MAIN = pd.read_excel(f'{path_data_files}/LVS_{sector_focus}_{region_focus}_{y_focus}_all_sources_concatinated.xlsx', index_col= None)

# PREWORK

if not os.path.exists(f'{path_plots}'):  # set directory and meta run txt file
    os.mkdir(f'{path_plots}')
with open(f'{path_plots}/Development_USD_sums_per_plot.txt', 'w') as f:  # setup txt file for numeric output
    f.write('\n')
    f.write('USD AMOUNT SUMED UP FOR EACH PLOT')
    f.write('\n')

# change country names for too long names in the plot
df_MAIN['country_name'][df_MAIN['country_name'] == 'Congo, Democratic Republic of the'] = 'Congo, D.Rep.'
df_MAIN['country_name'][df_MAIN['country_name'] == 'Central African Republic'] = 'Central Afr.Rep.'
df_MAIN['country_name'][df_MAIN['country_name'] == 'Tanzania, United Republic of'] = 'Tanzania, U.Rep.'
df_MAIN['country_name'][df_MAIN['country_name'] == 'Sao Tome and Principe'] = 'Sao Tome & Pr.'


# variables to compare to...
non_lvs_colnames = df_MAIN.columns.tolist()[17:99]
lvsUSD_colnames = ['dportal_all_USD', 'dportal_health_USD', 'china_invstm_all_USD', 'china_invstm_health_USD', 'china_constr_all_USD', 'china_constr_health_USD']

"""
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
"""

# BARPLOTS

fun_df_plot = df_MAIN.copy()
fields = ['dportal_all_USD', 'china_invstm_all_USD', 'china_constr_all_USD', 'pers_remittances_received_USD_2020']
colors = ['#1482faff',  '#ed4a0dff', '#9900ffff', '#ffd966ff']
colors_affiliate = ['#b4a7d6ff', '#d9d2e9ff', '#bde3ffff', '#1482faff', '#0b41cdff']

labels =['dportal projects', 'china investments', 'china constructions', 'global remittance']
cntry_column = 'country_name'
plot_title = 'Development Flows by data source (all sectors + remittance)'
export_TF = True
row_sum_value_TF = True
pcapita_TF = False

#overall plot settings
bar_width = 0.7
barfig_width = 6 #5 #7
barfig_height = 8 # 9
plt.rc('ytick', labelsize= 10)
plt.rc('xtick', labelsize= 10)
bar_label_size = 0.0001 #0.0001 #7
bar_label_color=  'white' #dimgray'
title_size = 13

barplot_x_axis_label = 'aid & development, million USD'

def barplot_stacked(fun_df_plot,fields, colors, labels, cntry_column, plot_title,  export_TF, row_sum_value_TF, colors_affiliate, pcapita_TF):
    df_plot = fun_df_plot.copy()

    if (not pcapita_TF):# | (not sector_focus == "ncd"):
        df_plot[fields] = df_plot[fields] / 1000000

    df_plot['row_sum'] = df_plot.loc[:, fields].sum(axis = 1)
    df_plot = df_plot[(df_plot['row_sum'] != np.inf) & (df_plot['row_sum'] >0) & ( np.invert( df_plot['roche_affiliate'].isna()) )] # include only greater 0 and no NaN
    df_plot_sorted = df_plot.sort_values(by = [ 'roche_affiliate_order', 'row_sum'], ascending = [False, True]).reset_index(drop = True).loc[:, (cntry_column.split()+ ['roche_affiliate', 'roche_affiliate_order', 'row_sum'] + fields)]
    # sort by row_sum of selected variables and order of Roche affiliates to form groups; keep only selected variables
    df_plot_sorted = df_plot_sorted.set_index(df_plot_sorted[f'{cntry_column}'])  # make label series to index of plot df


    fig, ax = plt.subplots(1, figsize=(barfig_width, barfig_height))
    #y_pos = range(0, df_plot_sorted.shape[0]*3, 3 )

    if not row_sum_value_TF:
        bottom_bar = df_plot_sorted[f'{fields[0]}'] * [0]
        i=3
        for i in range(0,len(fields)):
            """
            # vertical bars
            bar_container = ax.bar(df_plot_sorted[f'{cntry_column}'], df_plot_sorted[f'{fields[i]}'],
                                   width  =  bar_width, bottom=bottom_bar, align='center',
                                   label=f'{labels[i]}', color=f'{colors[i]}')
             """
            # horizontal bars
            bar_container = ax.barh(df_plot_sorted[f'{cntry_column}'], df_plot_sorted[f'{fields[i]}'],
                                    height =  bar_width, left = bottom_bar, align='center',
                                    label=f'{labels[i]}', color=f'{colors[i]}' )

            bottom_bar = bottom_bar + df_plot_sorted[f'{fields[i]}']

        # legend
        #plt.yticks(y_pos, df_plot_sorted[f'{cntry_column}'])
        plt.legend(labels, loc = 'lower right', ncol = 1, frameon=True)

    elif row_sum_value_TF:
        affiliate_list = df_plot_sorted['roche_affiliate'].unique().tolist()
        i_affiliate_list = affiliate_list[0]
        for i_affiliate_list in affiliate_list:
            subdf_plot_by_affiliate = df_plot_sorted.copy()
            subdf_plot_by_affiliate['row_sum'][ subdf_plot_by_affiliate['roche_affiliate'] != i_affiliate_list ] = 0
            bar_container = ax.barh(subdf_plot_by_affiliate[f'{cntry_column}'], subdf_plot_by_affiliate[f'row_sum'],
                                    height=bar_width, align='center',
                                    label=f'{i_affiliate_list}', color = colors_affiliate[affiliate_list.index(i_affiliate_list)] )
            c = ax.containers[0]
            x= c.datavalues
            x
            bar_container.datavalues
            #type(c.datavalues[0])
            #for c in ax.containers:
            if not pcapita_TF:
                bar_labels = [np.around(i, decimals = 1) for i in bar_container.datavalues]#c.datavalues]
                bar_labels = [v if v > 0 else "" for v in bar_labels]
                bar_labels = [f'{v}' if v != '' else '' for v in bar_labels]
                bar_labels
            elif pcapita_TF:
                bar_labels = [np.around(i, decimals = 1) for i in bar_container.datavalues]#c.datavalues]
                bar_labels = [v if v > 0 else "" for v in bar_labels]
                bar_labels = [f'{v}' if v != '' else '' for v in bar_labels]
                bar_labels

            ax.bar_label(bar_container,  labels=bar_labels, padding = 4, fontsize = bar_label_size, color = bar_label_color)

        if row_sum_value_TF:
            bar_legend_title = "Roche Entity"
        elif not row_sum_value_TF:
            bar_legend_title = ""
        ax.legend(affiliate_list, title =f'{bar_legend_title}', title_fontsize = 11, loc = 'lower right', ncol = 1, frameon=True)._legend_box.align = 'left'


    # PLOT FINISHES

    ax.set_title(f'{plot_title}\n', loc='left', fontsize = title_size)  # title

    # x axis
    ax.set_xlabel(f'{barplot_x_axis_label}')
    #if not pcapita_TF:
    #    pass
    #elif pcapita_TF:
    #    ax.set_xlabel(f'aid & development payments, USD')

    #for tick in ax.get_xticklabels():     # rotation of x ticks
    #    tick.set_rotation(90)

    # y axis
    plt.tight_layout()
    # bar labels in the plot
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
        plt.savefig(f'{path_plots}/{plot_title}.png')
        print(f'{plot_title} plot exported')
    elif not export_TF:
        print('')

    # export USD amount by txt file
    if not pcapita_TF: print_amount = ' M'
    elif pcapita_TF: print_amount = ''
    lines =  [f'{plot_title}']
    if not row_sum_value_TF:
        i_field = fields[0]
        for i_field in fields:
            print_sum = df_plot_sorted[i_field].sum()
            lines = lines + [f'by origin: for {i_field} USD{print_amount} {print_sum}']
        print_sum = df_plot_sorted['row_sum'].sum()
        lines = lines + [f'grand total for all countries: USD{print_amount} {print_sum}']

    elif row_sum_value_TF:
        affiliate_list = df_plot_sorted['roche_affiliate'].unique().tolist()
        i_affiliate_list = affiliate_list[0]
        for i_affiliate_list in affiliate_list:
            print_sum = df_plot_sorted['row_sum'][df_plot_sorted['roche_affiliate'] == i_affiliate_list].sum()
            lines = lines+  [f'by affiliates: for {i_affiliate_list} USD{print_amount} {print_sum}']
        print_sum = df_plot_sorted['row_sum'].sum()
        lines = lines + [f'grand total for all countries: USD{print_amount} {print_sum}']

    with open(f'{path_plots}/Development_USD_sums_per_plot.txt', 'a') as f:
        f.write('\n')
        for line in lines:
            f.write(line)
            f.write('\n')



df_plot_1 = df_MAIN.copy()
fields_1 = ['dportal_all_USD', 'china_invstm_all_USD', 'china_constr_all_USD', 'pers_remittances_received_USD_2020']
colors_1 = colors
labels_1 = ['dportal projects', 'china investments', 'china constructions', 'global remittance']
cntry_column_1 = 'country_name'
plot_title_1 = '1 Development Flows by affiliate (all sectors + remittance)'
export_TF_1  = True
row_sum_value_TF_1 = True
colors_affiliate_1 = colors_affiliate
pcapita_TF_1 = False
# all flows by affiliate (d-portal, china, remittance)
barplot_stacked(df_plot_1, fields_1, colors_1, labels_1, cntry_column_1, plot_title_1, export_TF_1, row_sum_value_TF_1, colors_affiliate_1 , pcapita_TF_1)

plot_title_12 = '2 Development Flows by data source (all sectors + remittance)'
# all flows by origin
barplot_stacked(df_plot_1, fields_1, colors_1, labels_1, cntry_column_1, plot_title_12, export_TF_1, False , colors_affiliate_1, pcapita_TF_1)


fields_13 = ['dportal_all_USD', 'china_invstm_all_USD', 'china_constr_all_USD']
labels_13 = ['dportal projects', 'china investments', 'china constructions']
plot_title_13= '3 Development Flows by affiliate (all sectors)'
plot_title_14= '4 Development Flows by data source (all sectors)'
#all flows without remittance
barplot_stacked(df_plot_1, fields_13, colors_1, labels_13, cntry_column_1, plot_title_13, export_TF_1, row_sum_value_TF_1, colors_affiliate_1, pcapita_TF_1 )


fields_15 = ['dportal_health_USD', 'china_invstm_health_USD', 'china_constr_health_USD']
labels_15 = ['dportal projects', 'china investments', 'china constructions']
plot_title_15= f'5 Development Flows by affiliate ({sector_focus})'
# health flows
barplot_stacked(df_plot_1, fields_15, colors_1, labels_15, cntry_column_1, plot_title_15, export_TF_1, row_sum_value_TF_1, colors_affiliate_1, pcapita_TF_1 )


df_plot_17 = df_MAIN.copy()
j_pop_tot = [s for s in df_MAIN.columns.tolist() if 'pop_tot' in s][0]
df_plot_17.loc[:, lvsUSD_colnames] = df_plot_17.loc[:, lvsUSD_colnames].div(df_plot_17.loc[:, [j_pop_tot]].iloc[:, 0], axis=0)
plot_title_17= f'7 Development Flows by affiliate ({sector_focus}, p capita (2020))'
pcapita_TF_17 = True
# health flows p capita
barplot_stacked(df_plot_17, fields_15, colors_1, labels_15, cntry_column_1, plot_title_17, export_TF_1, row_sum_value_TF_1, colors_affiliate_1, pcapita_TF_17 )


df_plot_19 = df_MAIN.copy()
j_gdp = [s for s in df_MAIN.columns.tolist() if 'GDP' in s][0]
df_plot_19.loc[:, lvsUSD_colnames] = df_plot_19.loc[:, lvsUSD_colnames].div(df_plot_19.loc[:, [j_gdp]].iloc[:, 0], axis=0)
df_plot_19.loc[:, lvsUSD_colnames] =df_plot_19.loc[:, lvsUSD_colnames]*1000000
plot_title_19= f'9 Development Flows by affiliate ({sector_focus}, relative to GDP (2020))'
pcapita_TF_19 = False
# health flows relative to GDP
barplot_stacked(df_plot_19, fields_15, colors_1, labels_15, cntry_column_1, plot_title_19, export_TF_1, row_sum_value_TF_1, colors_affiliate_1, pcapita_TF_19 )


fields_21 = ['dportal_health_USD']
colors_21 = ['#1482faff']
labels_21 =['dportal projects']
plot_title_21= f'21 Development Flows by affiliate ({sector_focus})'
pcapita_TF_21 = False
# ncds only
barplot_stacked(df_plot_1, fields_21, colors_21, labels_21, cntry_column_1, plot_title_21, export_TF_1, row_sum_value_TF_1, colors_affiliate_1, pcapita_TF_21 )




y_focus = f'2019'

df_MAIN_2019 = pd.read_excel(f'{path_data_files}/LVS_{sector_focus}_{region_focus}_{y_focus}_all_sources_concatinated.xlsx', index_col= None)



df_MAIN_2019['country_name'][df_MAIN_2019['country_name'] == 'Congo, Democratic Republic of the'] = 'Congo, Dem. Rep.'
df_MAIN_2019['country_name'][df_MAIN_2019['country_name'] == 'Central African Republic'] = 'Central African Rep.'
df_MAIN_2019['country_name'][df_MAIN_2019['country_name'] == 'Tanzania, United Republic of'] = 'Tanzania, United Rep.'
df_MAIN_2019['country_name'][df_MAIN_2019['country_name'] == 'Sao Tome and Principe'] = 'Sao Tome & Principe'

# SCATTERPLOTS

df_MAIN_2019.dtypes
fun_df_plot = df_MAIN_2019.copy()
fields = ['dportal_all_USD', 'china_invstm_all_USD', 'china_constr_all_USD']
fields2 = []
compare_field = ['GDP_USD_2019']
compare_label = []
colors_affiliate = ['#b4a7d6ff', '#d9d2e9ff', '#bde3ffff', '#1482faff', '#0b41cdff']
markers_affiliate = ['+', 's', 'v', 'D', 'o']
cntry_column = 'country_name'
plot_title = 'ASDFASDF'
log_values_TF = True
pcapita_TF = True
fun_print_xaxis = 'xaxis'
fun_print_yaxis = 'yaxis'
"""
#df_plot = df_plot.loc[:,lvsUSD_colnames] = df_plot_14.loc[:,lvsUSD_colnames].div(df_plot_14.loc[:,['pop_tot_2020']].iloc[:,0], axis = 0)
#labels = ['dportal all', 'china inv', 'china constr']#, 'global remittance']
#fields = ['dportal_health_USD', 'china_invstm_health_USD', 'china_health_all_USD']
#colors = ['#1482faff',  '#ed4a0dff', '#fac9b5ff', '#ffd966ff']
"""

#overall plot settings
scatterfig_width = 7 # 8
scatter_height = 7
scatter_marker_size = 50
scatter_label_size = 8
scatter_label_color = 'darkgray'
reg_color = 'firebrick'
reg_lw = 0.5
reg_style = 'dashed'
plot_reg_line_TF = True

plt.rc('ytick', labelsize=9)
plt.rc('xtick', labelsize=9)
#bar_label_size = 1
title_size = 13

def scatterplot_comparison(fun_df_plot, fields, compare_field, colors_affiliate, markers_affiliate, cntry_column, plot_title, log_values_TF, fun_print_xaxis, fun_print_yaxis, plot_reg_line_TF):
    df_plot = fun_df_plot.copy()
    df_plot.columns
    print_xaxis = fun_print_xaxis
    print_yaxis = fun_print_yaxis

    df_plot['row_sum'] = df_plot.loc[:, fields].sum(axis = 1)
    df_plot = df_plot[(df_plot['row_sum'] != np.inf) & (df_plot['row_sum'] >0) & ( np.invert( df_plot['roche_affiliate'].isna()) )] # include only greater 0 and no NaN
    df_plot_sorted = df_plot.sort_values(by = [ 'roche_affiliate_order', 'row_sum'], ascending = [False, True]).reset_index(drop = True).loc[:, (cntry_column.split()+ ['roche_affiliate', 'roche_affiliate_order', 'row_sum'] + fields + compare_field)]
    # sort by row_sum of selected variables and order of Roche affiliates to form groups; keep only selected variables
    df_plot_sorted = df_plot_sorted.set_index(df_plot_sorted[f'{cntry_column}'])  # make label series to index of plot df
    type(df_plot_sorted)
    df_plot_sorted

    fig, ax = plt.subplots(1, figsize=(scatterfig_width, scatter_height))

    if log_values_TF:
        df_plot_sorted[compare_field] = np.log(df_plot_sorted[compare_field])
        df_plot_sorted[f'row_sum'] = np.log(df_plot_sorted[f'row_sum'])
    scatter_labels = df_plot_sorted[cntry_column]
    affiliate_list = df_plot_sorted['roche_affiliate'].unique().tolist()

    i_affiliate_list = affiliate_list[0]
    i_affiliate_list
    for i_affiliate_list in affiliate_list:
        subdf_plot_by_affiliate = df_plot_sorted.copy()
        subdf_plot_by_affiliate = subdf_plot_by_affiliate[ subdf_plot_by_affiliate['roche_affiliate'] == i_affiliate_list ]
        scatter_container = ax.scatter(subdf_plot_by_affiliate[f'row_sum'],
                                       subdf_plot_by_affiliate[compare_field],
                                       label=f'{i_affiliate_list}',
                                       color = colors_affiliate[affiliate_list.index(i_affiliate_list)],
                                       marker =markers_affiliate[affiliate_list.index(i_affiliate_list)],
                                       alpha = 0.8, edgecolors = 'none', s = scatter_marker_size)
    label_txts=[]
    for i, txt in enumerate(scatter_labels):
        txt
        #ax.annotate(txt, ( df_plot_sorted.loc[:,f'{compare_field[0]}'][i], df_plot_sorted.loc[:,f'row_sum'][i]), fontsize = scatter_label_size )
        #ax.annotate(txt, ( df_plot_sorted.loc[:, f'row_sum'][i], df_plot_sorted.loc[:,f'{compare_field[0]}'][i]),fontsize=scatter_label_size)
        #plt.text(df_plot_sorted.loc[:, f'row_sum'][i], df_plot_sorted.loc[:,f'{compare_field[0]}'][i], txt, fontsize = scatter_label_size)
        label_txts.append(plt.text(df_plot_sorted.loc[:, f'row_sum'][i], df_plot_sorted.loc[:,f'{compare_field[0]}'][i], txt, fontsize = scatter_label_size, color = scatter_label_color))

    if plot_reg_line_TF: # add a regression line
        x = df_plot_sorted['row_sum'].to_numpy()
        y = df_plot_sorted[compare_field].to_numpy()
        x = x.reshape(len(x),)
        y=y.reshape(len(y),)
        idx = np.isfinite(x) & np.isfinite(y)
        b,m = np.polyfit(x[idx],y[idx],1)
        xseq = np.linspace(min(x[idx]), max(x[idx]), num=100)
        ax.plot(xseq,m + b* xseq, color = reg_color, lw = reg_lw, linestyle = reg_style)

        lines = []
        slope, intercept, r_value, p_value, std_err = stats.linregress(x[idx], y[idx])
        xy_corr, _ = pearsonr(x[idx], y [idx])
        xy_nobs = len(idx)
        lines =  lines + [f'title: {plot_title}', '\n', f'>> xy_corr= {xy_corr},  b0= {intercept}, b1= {slope}, pval= {p_value}, rsquared= {r_value**2}, xy_obs= {xy_nobs}','\n', '\n']

        if not os.path.exists(f'{path_plots}/scatter_plot_reg_outputs.txt'):
            with open(f'{path_plots}/scatter_plot_reg_outputs.txt', 'w') as f:  # setup txt file for numeric output
                lines.insert(0,'\n')
                lines.insert(0,'\n')
                lines.insert(0,'Regression outputs for Scatter plots')
                for line in lines:
                    f.write(line)
        elif os.path.exists(f'{path_plots}/scatter_plot_reg_outputs.txt'):
            with open(f'{path_plots}/scatter_plot_reg_outputs.txt', 'a') as f:  # setup txt file for numeric output
                for line in lines:
                    f.write(line)





    #  legend1 = ax.legend(*scatter.legend_elements(), loc="upper left", title="Entity")
    # ax.add_artist(legend1)
    ax.legend(affiliate_list, title = f'Roche Entity', title_fontsize= 11, loc = 'upper left', ncol = 1, frameon=True)._legend_box.align = 'left'


    # title
    ax.set_title(f'{plot_title}\n', loc='left', fontsize = title_size)

    # x axis
    # ax.set_xlabel(print_xaxis)
    #ax.set_xlabel(f'{compare_field[0]}')
    ax.set_ylabel(print_yaxis)


    # y axis
    #ax.set_ylabel('health donations USD')
    ax.set_xlabel(print_xaxis)
    plt.tight_layout()

    # bar labels in the plot
    # ax.bar_label(bar_container, rotation = 90, padding = 30) # label_type = 'center

    # remove spines
    #ax.spines['right'].set_visible(False)
    #ax.spines['left'].set_visible(False)
    #ax.spines['top'].set_visible(False)
    #ax.spines['bottom'].set_visible(False)

    # adjust limits and draw grid lines
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='gray', linestyle='dotted')
    ax.yaxis.grid(color='gray', linestyle='dotted')

    adjust_text(label_txts)

    #export plot
    plt.savefig(f'{path_plots}/{plot_title}.png')
    print(f'{plot_title} plot exported')



df_plot_50 = df_MAIN_2019.copy()
df_plot_51 = df_MAIN_2019.copy()
j_pop_tot = [s for s in df_MAIN_2019.columns.tolist() if 'pop_tot' in s][0]
df_plot_51.loc[:, lvsUSD_colnames] = df_plot_51.loc[:, lvsUSD_colnames].div(df_plot_51.loc[:, [j_pop_tot]].iloc[:, 0], axis=0)
fields_51 = ['dportal_health_USD', 'china_invstm_health_USD', 'china_constr_health_USD']
colors_affiliate_51 = ['#b4a7d6ff', '#d9d2e9ff', '#bde3ffff', '#1482faff', '#0b41cdff']
markers_affiliate_51 = ['P', 's', 'v', 'D', 'o']
cntry_column_51 = 'country_name'

compare_field_51 = ['ext_hex_pcap_USD_2019']
plot_xaxis_51 = 'Health donations (USD) per capita'
plot_yaxis_51 = 'External health expenditures (USD) per capita'
plot_title_51 = f'51 {sector_focus} expenditures to donations per capita'
log_values_TF_51 = False
plot_regline_TF_51 = False
#scatterplot_comparison(df_plot_51, fields_51, compare_field_51, colors_affiliate_51, markers_affiliate_51, cntry_column_51, plot_title_51, log_values_TF_51, plot_xaxis_51, plot_yaxis_51, plot_regline_TF_51)


plot_xaxis_52 = 'log Health donations (USD) per capita'
plot_yaxis_52 = 'log External health expenditures (USD) per capita'
plot_title_52 = f'52 {sector_focus} expenditures to donations per capita (log)'
log_values_TF_52 = True
plot_regline_TF_52 = True
scatterplot_comparison(df_plot_51, fields_51, compare_field_51, colors_affiliate_51, markers_affiliate_51, cntry_column_51, plot_title_52, log_values_TF_52, plot_xaxis_52, plot_yaxis_52 , plot_regline_TF_52)


compare_field_53 = ['gov_hex_pcap_USD_2019']
plot_yaxis_53 = 'log Government health expenditures (USD) per capita'
plot_title_53 = f'53 {sector_focus} gov to lvs comparison'
#scatterplot_comparison(df_plot_51, fields_51, compare_field_53, colors_affiliate_51, markers_affiliate_51, cntry_column_51, plot_title_53, log_values_TF_52, plot_xaxis_52, plot_yaxis_53, plot_regline_TF_52)


compare_field_54 = ['private_hex_pcap_USD_2019']
plot_yaxis_54 = 'log Private health expenditures (USD) per capita'
plot_title_54 = f'54 {sector_focus} priv to lvs comparison'
#scatterplot_comparison(df_plot_51, fields_51, compare_field_54, colors_affiliate_51, markers_affiliate_51, cntry_column_51, plot_title_54, log_values_TF_52, plot_xaxis_52, plot_yaxis_54, plot_regline_TF_52)


compare_field_55 = ['oop_hex_pcap_USD_2019']
plot_yaxis_55 = 'log Out-of-Pocket health expenditures (USD) per capita'
plot_title_55 = f'55 {sector_focus} oop to lvs comparison'
#scatterplot_comparison(df_plot_51, fields_51, compare_field_55, colors_affiliate_51, markers_affiliate_51, cntry_column_51, plot_title_55, log_values_TF_52, plot_xaxis_52, plot_yaxis_55, plot_regline_TF_52)



df_plot_60 = df_MAIN_2019.copy()
j_pop_tot = [s for s in df_MAIN_2019.columns.tolist() if 'pop_tot' in s][0]
df_plot_60.loc[:, lvsUSD_colnames] = df_plot_60.loc[:, lvsUSD_colnames].div(df_plot_60.loc[:, [j_pop_tot]].iloc[:, 0], axis=0)
j_oop_hex     = [s for s in df_MAIN_2019.columns.tolist() if 'oop_hex_pcap' in s][0]
j_private_hex = [s for s in df_MAIN_2019.columns.tolist() if 'private_hex_pcap' in s][0]
df_plot_60['d_private_to_oop_hex_pcap_USD'] = df_plot_60.loc[:, [j_private_hex]].iloc[:, 0] - df_plot_60.loc[:, [j_oop_hex]].iloc[:, 0]

fields_60 = ['dportal_health_USD', 'china_invstm_health_USD', 'china_constr_health_USD']
compare_field_60 = ['d_private_to_oop_hex_pcap_USD']
plot_xaxis_60 = 'Health donations (USD) per capita'
plot_yaxis_60 = 'Delta Private -  Out of Pocket health expenditures (USD) per capita'
log_values_TF_60 = False
plot_title_60 = f'60 Out-of-Pocket gap to {sector_focus} donations'
#scatterplot_comparison(df_plot_60, fields_60, compare_field_60, colors_affiliate_51, markers_affiliate_51, cntry_column_51, plot_title_60, log_values_TF_60, plot_xaxis_60, plot_yaxis_60, plot_regline_TF_52)


df_plot_61 = df_plot_60[df_plot_60['country_name'] !='South Africa']
plot_title_61 = f'61 Out-of-Pocket gap to {sector_focus} donations (excluding South Africa as outlier)'
#scatterplot_comparison(df_plot_61, fields_60, compare_field_60, colors_affiliate_51, markers_affiliate_51, cntry_column_51, plot_title_61, log_values_TF_60, plot_xaxis_60, plot_yaxis_60, plot_regline_TF_52)


plot_xaxis_62 = 'log Health donations (USD) per capita'
plot_title_62 = f'Out-of-Pocket gap to {sector_focus} donations logged (excluding South Africa as outlier) (log)'
plot_yaxis_62 = 'log Delta Private, Out of Pocket health expenditures (USD) per capita'
log_values_TF_62 = True
#scatterplot_comparison(df_plot_60, fields_60, compare_field_60, colors_affiliate_51, markers_affiliate_51, cntry_column_51, plot_title_62, log_values_TF_62, plot_xaxis_62, plot_yaxis_62, plot_reg_line_TF_51)


df_plot_60[fields_60].sum()
print(tabulate(df_plot_60, headers='keys', tablefmt='psql'))

writer = pd.ExcelWriter(f'{path_files}/{name_files}_concatPY.xlsx', engine='xlsxwriter')
df_fdi.to_excel(writer, sheet_name= 'fDiMarkets', index=False)
df_fdi_conc.to_excel(writer, sheet_name= 'concatinated_data_by_python', index=False)
writer.save()
time.sleep(1)
writer.close()



"""
       'pop_tot_2019', 'pop_growth_perc_2019', 'age_dep_rat_tot_2019', 'age_dep_rat_old_2019', 'age_dep_rat_young_2019', 'hex_perc_gdp_2019',
       'gov_hex_perc_gdp_2019', 'GDP_USD_2019', 'GDP_ann_growth_perc_2019', 'hex_pcap_USD_2019', 'financial_sect_rating_2019',
       'corruption_rating_2019', 'gov_hex_pcap_USD_2019', 'gov_hex_perc_of_hex_tot_2019', 'private_hex_perc_of_hex_tot_2019',
       'private_hex_pcap_USD_2019', 'ext_hex_pcap_USD_2019', 'ext_hex_perc_of_hex_tot_2019', 'Life_expec_tot_years_2019',
       'oop_hex_perc_of_hex_tot_2019', 'oop_hex_pcap_USD_2019',  'physicians_p1000cap_2019',
"""







"""
print(tabulate(df_MAIN[df_MAIN['country_name']=='Algeria'], headers='keys', tablefmt='psql'))
print(tabulate(df_plot_51[df_plot_51['country_name']=='Algeria'], headers='keys', tablefmt='psql'))
"""

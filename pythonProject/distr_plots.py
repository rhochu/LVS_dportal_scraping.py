# PACKAGE INSTALLATION
import os as os

import expression as expression
import numpy as np
import pandas as pd
import matplotlib
import warnings

from tabulate import tabulate
from plotnine import *
from plotnine import ggplot, aes, geom_point
warnings.filterwarnings('ignore')


# FUNCTIONS
def quantile_exc(ser, q):
    ser_sorted = ser.sort_values()
    rank = q * (len(ser) + 1) - 1
    assert rank > 0, 'quantile is too small'
    rank_l = int(rank)
    return ser_sorted.iat[rank_l] + (ser_sorted.iat[rank_l + 1] -
                                     ser_sorted.iat[rank_l]) * (rank - rank_l)


# SET WD & IMPORT DATA

os.getcwd()
os.listdir()
# wd_path = r'G:\My Drive\2_EXPGA\Quant_Africa\work laura + bruno'
# os.chdir(wd_path)
# del wd_path
# print('=> WORKING directory: ', pathlib.Path().resolve())
# print('=> script directory: ', pathlib.Path(__file__).parent.resolve())

df = pd.read_excel(r'G:\My Drive\2_EXPGA\Quant_Africa\work laura + bruno\COPY_RH_Africa_Country Prioritization Matrix V2.xlsm',sheet_name= 'Data Input for R')
print(df)
print(tabulate(df, headers='keys', tablefmt='psql'))

# harmonize headers
type(df)
df.dtypes
df['Country Population'] = df['Country Population'].astype("float")
df['Corruption Index'] = df['Corruption Index'].astype("float")
df['Roche Patients'] = df['Roche Patients'].astype("float")
df.dtypes

df.columns
type(df.columns)
col_names_old =  df.columns.tolist()
col_names_new =  [w.replace(' ', '_') for w in col_names_old]
col_names_new2 = [c.lower() for c in col_names_new]
df = df.set_axis(col_names_new2, axis='columns')
df.columns
del col_names_old, col_names_new, col_names_new2

df = df.fillna(0)

print(tabulate(df, headers='keys', tablefmt='psql'))


# OVERALL IDENTIFIERS AND IMPORTANT VARIABLES
par_names = df.columns.values
names_market_attr = par_names.tolist()[1:9]
names_bus_potent = par_names.tolist()[9:]
par_names


# ADD LOG VALUES + QUANTILE SCORES + PLOT
export_distr_plots_by_QUINT =     False
export_distr_plots_by_QUINT_LOG = False

# adding log values
for i in range(1,len(par_names),1):
    j: int = df.columns.get_loc(par_names[i])
    print(f'Add LOG value: i is {i}, for name: {par_names[i]}; j is {j}')
    df.insert(loc=j + 1, column=f'{par_names[i]}_LOG', value=np.nan)
    df.iloc[:, j + 1] = np.log(df.iloc[:, j])
    del i,j

# add qunit scores
for i in range(1,len(par_names),1):
    j: int = df.columns.get_loc(par_names[i])
    print(f'Add QUINT scores: i is {i}, for name: {par_names[i]}; j is {j}')

    df.insert(loc=j + 1, column=f'{par_names[i]}_score_QUINT', value=np.nan)

    df.iloc[df.iloc[:, j].between(0, quantile_exc(df.iloc[:, j], 0.2), 'left').values, j + 1] = '1'
    df.iloc[df.iloc[:, j].between(quantile_exc(df.iloc[:, j], 0.2), quantile_exc(df.iloc[:, j], 0.4),'left').values, j + 1] = '2'
    df.iloc[df.iloc[:, j].between(quantile_exc(df.iloc[:, j], 0.4), quantile_exc(df.iloc[:, j], 0.6),'left').values, j + 1] = '3'
    df.iloc[df.iloc[:, j].between(quantile_exc(df.iloc[:, j], 0.6), quantile_exc(df.iloc[:, j], 0.8),'left').values, j + 1] = '4'
    df.iloc[df.iloc[:, j].between(quantile_exc(df.iloc[:, j], 0.8), np.inf, 'left').values, j + 1] = '5'

    df.iloc[:,j+1] = pd.Series(df.iloc[:,j+1], dtype = "category")

    del i, j
df.dtypes
print(tabulate(df, headers='keys', tablefmt='psql'))

# PLOT DISTRIBUTIONS
export_distr_plots_by_QUINT
if export_distr_plots_by_QUINT:
    for i in range(1, len(par_names), 1):
        print(f'Export scatter plot: {i}, {par_names[i]}')
        p = (
                ggplot(df, aes(x=f'reorder(country, {par_names[i]})', y=f'{par_names[i]}', color=f'{par_names[i]}_score_QUINT')) +
                geom_point() +
                theme_bw() +
                theme(axis_text_x=element_text(rotation=90, hjust=1, size=7))
        )
        ggsave(p, f'G:\\My Drive\\2_EXPGA\\Quant_Africa\\distr_plots_priomatrix\\{par_names[i]}_quint.png')

        del i, p
else:
    print(f'plots not exported')

export_distr_plots_by_QUINT_LOG
if export_distr_plots_by_QUINT_LOG:
    for i in range(1, len(par_names), 1):
        print(f'Export LOG scatter plot: {i}, {par_names[i]}')
        p = (
                ggplot(df, aes(x=f'reorder(country, {par_names[i]})', y=f'{par_names[i]}', color=f'{par_names[i]}_score_QUINT')) +
                geom_point() +
                scale_y_continuous(trans='log2') +
                theme_bw() +
                theme(axis_text_x=element_text(rotation=90, hjust=1, size=7))

        )
        ggsave(p, f'G:\\My Drive\\2_EXPGA\\Quant_Africa\\distr_plots_priomatrix\\{par_names[i]}_quint_LOG.png')

        del i, p
else:
    print(f'plots not exported')


# create weight vectors
weights_market_attr = [0.1, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1]
weights_bus_potent =  [0.35, 0.1, 0.1, 0.15, 0.15, 0.1, 0.05]

sum(weights_market_attr)
for i in range(len(weights_market_attr)):
    print(f'>> weight: {weights_market_attr[i]} {names_market_attr[i]}')
print('\n')
sum(weights_bus_potent)
for i in range(len(weights_bus_potent)):
    print(f'>> weight: {weights_bus_potent[i]} {names_bus_potent[i]}')



# BUBBLE CHART WITH STAND SCORE
classification_method = "_score_QUINT"
omit_country = ['South Africa', 'Algeria', 'Nigeria', 'Morocco', 'Libya', 'Tunisia', 'Mauritius', 'Seychelles', 'Botswana', 'Namibia']
export_bubble_plots_by_QUINT = True

def kick_one_out(fun_df, fun_suffix, fun_omit_country):

    # kickout the omitted countries
    ~fun_df.country.isin(omit_country)
    fun_df = fun_df[~fun_df.country.isin(omit_country)]

    # add STAND values
    for i in range(1,len(par_names),1):
        j: int = fun_df.columns.get_loc(par_names[i])
        print(f'Add STAND scores: i is {i}, for name: {par_names[i]}; j is {j}')

        fun_df.insert(loc=j + 1, column=f'{par_names[i]}_score_STAND', value=np.nan)
        fun_df.iloc[:,j+1] = fun_df.iloc[:,j] / fun_df.iloc[:,j].sum(axis=0, skipna=True)
        del i, j

    fun_sub_df = pd.DataFrame(fun_df.country, columns = ['country', 'market_attr', 'bus_potent'])

    id_market_attr = fun_df.columns.isin([name + "_score_STAND" for name in names_market_attr])
    fun_sub_df.market_attr = np.sum(fun_df.iloc[:, id_market_attr] * weights_market_attr, axis=1)
    id_bus_potent = fun_df.columns.isin([name + "_score_STAND" for name in names_bus_potent])
    # fun_df.iloc[:, id_bus_potent] = 1
    fun_sub_df.bus_potent = np.sum(fun_df.iloc[:, id_bus_potent] * weights_bus_potent, axis=1)

    return fun_sub_df
sub_df = kick_one_out(df, classification_method, omit_country)


# select country to be dropped next
sub_df['sum_axises'] =sub_df.market_attr / np.sum(sub_df.market_attr) +  sub_df.bus_potent / np.sum(sub_df.bus_potent)
sub_df['color_indicator'] = sub_df.country.isin([sub_df.sort_values('sum_axises').iloc[-1,0]])
sub_df.sort_values('sum_axises').iloc[:,:]


if export_bubble_plots_by_QUINT:
    p = (
            ggplot(sub_df, aes(x='bus_potent', y='market_attr', label = 'country', color = 'color_indicator', size=3)) +
            geom_point(alpha=0.5,) +
            geom_label() +
            scale_color_manual(values=['black', 'red']) +
            theme(legend_position= 'none')
    )
    #ggsave(p, f'G:\\My Drive\\2_EXPGA\\Quant_Africa\\bubble_chart{classification_method}_{len(omit_country)}.png')
    ggsave(filename = f'G:\\My Drive\\2_EXPGA\\Quant_Africa\\bubble_chart{classification_method}_{len(omit_country)}.png',
           plot = p,
           scale = 5,
           width = 30,
           height = 17.5,
           dpi = 200,
           units = 'cm')

else:
    print(f'plots not exported')

np.sum(sub_df, axis=0)
p

print(tabulate(sub_df, headers='keys', tablefmt='psql'))
print(f' run last line successfully :)) ')


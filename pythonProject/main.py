import os as os

import tabula
from tabula import read_pdf
from tabulate import tabulate

os.getcwd()
os.listdir()
# df = read_pdf('wir_fs_ng_en.pdf', pages = 'all', multiple_tables=True)
dfs = tabula.read_pdf('wir_fs_ng_en.pdf', pages = 2)




print(df)
import pandas as pd
from pandas import DataFrame

# Cleans the files before initial pandas import
def pre_clean(f):

  print('[INFO] Pre-Cleaning ', f.split('/')[-1], end='')

  f_cleaned = ""

  with open(f, 'r', encoding='iso-8859-15') as file:
    f_cleaned = file.read().replace('"', '')

  with open(f, 'w', encoding='iso-8859-15') as file:
    file.write(f_cleaned)

  print(' (Finished)')
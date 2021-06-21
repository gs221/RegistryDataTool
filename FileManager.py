from numpy import result_type, spacing
import pandas as pd
from pandas import DataFrame
import os

# Cleans the files before initial pandas import
def pre_clean(f):

  print('[INFO] Pre-Cleaning ', f.split('/')[-1], end='')

  f_cleaned = ''

  with open(f, 'r', encoding='iso-8859-15') as file:
    f_cleaned = file.read().replace('"', '')

  with open(f, 'w', encoding='iso-8859-15') as file:
    file.write(f_cleaned)

  print(' (Finished)')

def format_scl(f):

  print('[INFO] Formatting SCL Data in', f, end='')

  # Check results file has been created 
  if not os.path.isfile(f):
    print('[ERROR] Results file does not exist or could not be found.')
    exit(0)

  # Import results data into pandas
  results: DataFrame = pd.read_csv(f, sep=',', dtype=str, keep_default_na=False)

  # Make all columns uppercase
  results = results.apply(lambda x: x.str.upper())

  # Make email and Fax number columns lower case
  results['Email address'] = results['Email address'].str.lower()
  results['Fax number'] = results['Fax number'].str.lower()
  
  print(' (Finished)')

  #extract_new_ucas(results)

  results.to_csv('results.csv', index=False)

def extract_new_ucas(df: DataFrame):
  print('[INFO] Extracting potential new UCAS schools into new_ucas.csv', end='')

  # Get ucas column names 
  scl_column = df.loc[:, 'School code': 'EDUBASE URN'].columns
  ucas_column = df.loc[:, 'School': 'Merged with school code'].columns

  df.dropna(axis=0, how='all', subset=scl_column, inplace=True)
  df.dropna(axis=0, how='all', subset=ucas_column, inplace=True)

  print(df.to_csv('test.csv'))

  print(' (Finished)')

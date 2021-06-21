from numpy import spacing
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

  # Check results file has been crated 
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

  results.to_csv('results.csv', index=False)
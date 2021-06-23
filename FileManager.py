import os
import pandas as pd
from pandas import DataFrame

# Cleans the files before initial pandas import
def pre_clean(f):

  print('[INFO] Pre-Cleaning ', f.split('/')[-1], end='')

  f_cleaned = ''

  with open(f, 'r', encoding='iso-8859-15') as file:
    f_cleaned = file.read().replace('"', '')

  with open(f, 'w', encoding='iso-8859-15') as file:
    file.write(f_cleaned)

  print(' (Finished)')

def format_results(m, s, u):

  print('[INFO] Formatting results data.', end='')

  # Check results file has been created 
  if not (os.path.isfile(m) and os.path.isfile(s) and os.path.isfile(u)):
    print('[ERROR] Could not locate results files.')
    exit(0)

  # Import results data into pandas
  potential_matches: DataFrame = pd.read_csv(m, sep=',', dtype=str, keep_default_na=False)
  scl_only: DataFrame = pd.read_csv(s, sep=',', dtype=str, keep_default_na=False)
  ucas_only: DataFrame = pd.read_csv(u, sep=',', dtype=str, keep_default_na=False)

  # Make all columns uppercase in all files
  potential_matches = potential_matches.apply(lambda x: x.str.upper())
  scl_only = scl_only.apply(lambda x: x.str.upper())
  ucas_only = ucas_only.apply(lambda x: x.str.upper())

  # Make email and Fax number columns lower case in the potential matches and scl files
  potential_matches['Email address'] = potential_matches['Email address'].str.lower()
  potential_matches['Fax number'] = potential_matches['Fax number'].str.lower()

  scl_only['Email address'] = scl_only['Email address'].str.lower()
  scl_only['Fax number'] = scl_only['Fax number'].str.lower()
  
  print(' (Finished)')

  # Write formatted tables to files 
  potential_matches.to_csv('potential_matches.csv', index=False)
  scl_only.to_csv('scl_only.csv', index=False)
  ucas_only.to_csv('ucas_only.csv', index=False)


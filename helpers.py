"""
File Helpers: 

Contains functions that are frequently used. 
"""

import os
import sys
import json

import pandas as pd
from pandas import DataFrame

from json.decoder import JSONDecodeError

def pre_clean(f):
  """ Removes any quotation marks from the files to prevent errors during importation. """

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


def open_config_file(config_path: str) -> dict:
  """ Attempts to open and parse the supplied configuration file. Returns dictionary containing configuration. """

  try: 
    with open(config_path, 'r') as config_file:   
      return json.load(config_file)                
  except FileNotFoundError:
    print('[ERROR] Could not find configuration file ' + config_path + '.')
    sys.exit(1)
  except JSONDecodeError:
    print('[ERRROR] Could not parse ' + config_path + '. Please ensure it contains only valid JSON.')
    sys.exit(1)


def try_again() -> None:
    """ Prompts the user to retry some process or exit program """

    while True:
        value = input("Enter 't' to try again or 'c' to exit. ").lower()
        if value == 't': return
        if value == 'c': sys.exit(0) 
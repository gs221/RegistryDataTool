"""
File Helpers: 

Contains functions that are frequently used. 
"""

import os
import sys
import json
from colorama.ansi import AnsiFore

import pandas as pd
from pandas import DataFrame
from colorama import Fore

from json.decoder import JSONDecodeError

def pre_clean(f):
  """ Removes any quotation marks from the files to prevent errors during importation. """

  print(coloured('[INFO]', Fore.GREEN) + ' Pre-Cleaning ', f.split('/')[-1], end='')

  f_cleaned = ''

  with open(f, 'r', encoding='iso-8859-15') as file:
    f_cleaned = file.read().replace('"', '')

  with open(f, 'w', encoding='iso-8859-15') as file:
    file.write(f_cleaned)

  print(' (Finished)')


def open_config_file(config_path: str) -> dict:
  """ Attempts to open and parse the supplied configuration file. Returns dictionary containing configuration. """

  try: 
    with open(config_path, 'r') as config_file:   
      return json.load(config_file)                
  except FileNotFoundError:
    print_err('Could not find configuration file ' + config_path + '.')
  except JSONDecodeError:
    print_err('Could not parse ' + config_path + '. Please ensure it contains only valid JSON.')
    

def try_again() -> None:
    """ Prompts the user to retry some process or exit program """

    while True:
        value = input("Enter 't' to try again or 'e' to exit. ").lower()
        if value == 't': return
        if value == 'e': sys.exit(0) 


def csv_to_upper(file_path: str, exclude=[]) -> None:
  """ Converts every column to uppercase in given file excluding column names set to exclude. """

  # Check that file exists 
  if not os.path.isfile(file_path):
    print_err('Could not locate \'' + file_path + '\'. Formatting could not be performed.')

  # Print informative message to user
  print(coloured('[INFO] ', Fore.GREEN) + 'Formatting ' + file_path + '.', end='')
  
  # If columns have been given to exclude from formatting, print columns
  if exclude:
    print(' Excluding columns: ', end='')
    print(*exclude, sep=', ', end='')
    print('.', end='')

  # Import file into pandas
  file_data: DataFrame = pd.read_csv(file_path, sep=',', dtype=str, keep_default_na=False)

  # Make all columns uppercase in all files
  file_data = file_data.apply(lambda x: x.str.upper())

  # Convert excluded columns back to lowercase
  for column in exclude:
    file_data[column] = file_data[column].str.lower()

  # Write formatted tables to file
  file_data.to_csv(file_path, index=False)

  print(' (Finished)')


def print_err(msg: str) -> None:
  """ Prints supplied error message and sys.exits(1) """
  print(coloured('[ERROR] ', Fore.RED) + msg)
  sys.exit(1)

def coloured(string: str, colour: AnsiFore) -> str:
  """ returns string with colour information surrounding. """
  return colour + string + Fore.RESET
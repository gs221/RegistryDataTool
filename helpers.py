"""
File Helpers: 

Contains helpful functions that are frequently used. 
"""

import os
import shutil
import sys
import json

import pandas as pd
from pandas import DataFrame
from colorama import Fore
from json.decoder import JSONDecodeError
from colorama.ansi import AnsiFore
from colorama.initialise import deinit

def pre_clean(f):
  """ Removes any quotation marks from the files to prevent errors during importation. """

  info('Pre-Cleaning ' + f.split('/')[-1], fin='')    # Prints info message and gets filename from file path. 

  f_cleaned = ''                                     

  with open(f, 'r', encoding='iso-8859-15') as file:  # Opens file with appropriate encoding (for read) 
    f_cleaned = file.read().replace('"', '')          # Replaces all quotation marks with nothing

  with open(f, 'w', encoding='iso-8859-15') as file:  # Opens file with appropriate encoding (for write)
    file.write(f_cleaned)                             # Writes cleaned file to file

  print(' (Finished)')


def open_config_file(config_path: str) -> dict:
  """ Attempts to open and parse the supplied configuration file. Returns dictionary containing configuration. """

  try: 
    # Tries to read and parse configuration file from given path.
    with open(config_path, 'r') as config_file:   
      return json.load(config_file)                

  except FileNotFoundError:
    # If the file could not be found, print  meaningful error message. 
    error('Could not find configuration file ' + config_path + '.')

  except JSONDecodeError:
    # if the file could not be parsed (contains invalid JSON) then pring error message. 
    error('Could not parse ' + config_path + '. Please ensure it contains only valid JSON.')
    

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
    error('Could not locate \'' + file_path + '\'. Formatting could not be performed.')

  # Print informative message to user
  info('Formatting ' + file_path + '.', fin='')
  
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


def error(msg: str, fin=None, pre='', post='') -> None:
  """ Prints supplied error message and sys.exits(1) """
  print(coloured(pre + '[ERROR] ', Fore.RED) + msg + post, end=fin)
  cleanup_and_exit()


def todo(msg: str, fin=None, pre='', post='') -> None:
  """ Prints supplied todo message. """
  print(pre + coloured('[TODO] ', Fore.YELLOW) + msg + post, end=fin)


def info(msg: str, fin=None, pre='', post='') -> None:
  """ Prints supplied info message. """
  print(pre + coloured('[INFO] ', Fore.GREEN) + msg + post, end=fin)


def coloured(string: str, colour: AnsiFore) -> str:
  """ returns string with colour information surrounding. """
  return colour + string + Fore.RESET


def cleanup_and_exit(prompt=True) -> None:
  """ Cleans stuff before exiting. """

  # Disarm colorama
  deinit()

  # Remove temporary directories 
  if os.path.exists('./data/training'): shutil.rmtree('./data/training')
  if os.path.exists('./data/cleaned'): shutil.rmtree('./data/cleaned')

  # Exit program
  if prompt: input('Press enter to exit ')
  sys.exit(0)
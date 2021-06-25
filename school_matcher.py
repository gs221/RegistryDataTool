"""
School Matcher:

Contains functions that match schools accross two csv files. 

"""

import os
import shutil

from pandas.core.frame import DataFrame
from helpers import csv_to_upper, open_config_file, print_err
from csv_dedupe import csv_link

# Filepaths and filenames
configuration_path = './configurations/option_one_config.json'


def match_schools(ucas: DataFrame, scl: DataFrame) -> None:
  """ Matches schools that are in two csv files. """

  # Open and store configuration information from supplied file. 
  configuration = open_config_file(configuration_path)

  # Generate files for linker 
  generate_clean_files(ucas, scl, configuration)

  # Find Matches
  linker = csv_link.CsvLink(configuration)
  linker.run()

  # Remove cleaned directory as it is no longer required
  remove_directory(configuration.get('input_path'))

  # Get paths to results files from configuration 
  potential_matches = configuration.get('matches_file')
  ucas_only = configuration.get('ucas_only_file')
  scl_only = configuration.get('scl_only_file')

  # Format results to uppercase, excluding set columns
  csv_to_upper(potential_matches, exclude=['Fax number', 'Email address'])
  csv_to_upper(scl_only, exclude=['Fax number', 'Email address'])
  csv_to_upper(ucas_only)
 

def generate_clean_files(ucas: DataFrame, scl: DataFrame, config: dict) -> None:
  """ Takes data frame produced by pandas, extracts unneccesary records and exports clean csv files to be used by duplicate finder."""

  # Remove records from UCAS data where corresponding school with ID is already in scl data
  removed_common = ucas[ucas['School'].isin(scl['School code']) == False]

  # Remove UCAS codes and other malformed codes leaving only internal codes
  without_ucas = scl[scl['School code'].str.contains(r'^[a-zA-Z]{2}\d{3,5}$', na=False)]

  # Get path and filenames from configuration 
  cleaned_csv_path = config.get('input_path')
  
  if len(config['input']) == 2:
    scl_cleaned = config['input'][0]
    ucas_cleaned = config['input'][1]
  else: 
    print_err('[ERROR] You must supply two input paths in configuration file.')

  # Generate directory for pandas generated csv files
  if not os.path.exists(cleaned_csv_path):
      os.mkdir(cleaned_csv_path)
  else:
      shutil.rmtree(cleaned_csv_path)
      os.mkdir(cleaned_csv_path)

  # Generate files and place in directory
  removed_common.to_csv(cleaned_csv_path + ucas_cleaned, index=False)
  without_ucas.to_csv(cleaned_csv_path + scl_cleaned, index=False)


def remove_directory(path: str) -> None:
  """ Removes supplied directory/folder. """
  if os.path.exists(path):
    shutil.rmtree(path)
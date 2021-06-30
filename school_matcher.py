"""
School Matcher:

Contains functions that match schools accross two csv files. 

"""

import os

from csv_dedupe import csv_link
from pandas.core.frame import DataFrame
from helpers import csv_to_upper, open_config_file

# Filepaths and filenames
cleaned_csv_path = './data/cleaned/'
ucas_cleaned = 'ucas_for_option1.csv'
scl_cleaned = 'scl_for_option1.csv'

def match_schools(ucas: DataFrame, scl: DataFrame, config_path: str) -> None:
  """ Matches schools that are in two csv files. """

  # Generate files for linker, using these files prevents any decoding errors. 
  generate_clean_files(ucas, scl)

  # Open and store configuration information from supplied file. 
  configuration = open_config_file(config_path)

  # Add input file paths to configuration, this is used by csv_link.py to determine the two input filenames. 
  configuration['input'] = [cleaned_csv_path + scl_cleaned, cleaned_csv_path + ucas_cleaned]

  # Find Matches
  # Creates instance of and runs the linker program with the given configuration 
  linker = csv_link.CsvLink(configuration)
  linker.run()

  # Get paths to results files from configuration 
  potential_matches = configuration.get('matches_file')
  ucas_only = configuration.get('ucas_only_file')
  scl_only = configuration.get('scl_only_file')

  # Format results to uppercase, excluding set columns
  csv_to_upper(potential_matches, exclude=['Fax number', 'Email address'])
  csv_to_upper(scl_only, exclude=['Fax number', 'Email address'])
  csv_to_upper(ucas_only)
 

def generate_clean_files(ucas: DataFrame, scl: DataFrame) -> None:
  """ Takes data frame produced by pandas, extracts unneccesary records and exports clean csv files to be used by duplicate finder."""

  # Remove records from UCAS data where corresponding school with ID is already in scl data
  removed_common = ucas[ucas['School'].isin(scl['School code']) == False]

  # Remove UCAS codes and other malformed codes leaving only internal codes
  without_ucas = scl[scl['School code'].str.contains(r'^[a-zA-Z]{2}\d{3,5}$', na=False)]

  # Generate directory for pandas generated csv files
  if not os.path.exists(cleaned_csv_path):
      os.mkdir(cleaned_csv_path)

  # Generate clean files and place in directory
  # Index is set to false to prevent pandas from writiting the ID's it has given to each row. 
  removed_common.to_csv(cleaned_csv_path + ucas_cleaned, index=False)
  without_ucas.to_csv(cleaned_csv_path + scl_cleaned, index=False)



"""
DuplicateDetector.py

This file contains the functions that are used to identify suplicate schools in a single csv file. 

"""

import csv_dedupe
import os
import shutil

from pandas import DataFrame
from csv_dedupe import csv_dedupe
from helpers import csv_to_upper, open_config_file, error

# Path for cleaned file to be stored 
cleaned_csv_path = './data/cleaned/'

def detect_duplicates(data: DataFrame, config_path: str) -> None:
  """ Detects duplicates in a singe csv file. """

  # Open and store configuration information from supplied file. 
  configuration = open_config_file(config_path)

  # Generate input filename based on selection
  file_type = configuration.get('file_type', None)

  if file_type == 'ucas': cleaned_file_name = 'ucas_for_option2.csv'
  elif file_type == 'scl': cleaned_file_name = 'scl_for_option3.csv'
  else: error('Malformed configuration file.')

  # Generate clean file from data for dedupe 
  generate_clean_file(data, cleaned_file_name)

  # Add input file path to configuration
  configuration['input'] = cleaned_csv_path + cleaned_file_name

  # Find duplicates
  deduper = csv_dedupe.CsvDedupe(configuration)
  deduper.run()

  # Remove cleaned directory as it is no longer required
  if os.path.exists(cleaned_csv_path):
    shutil.rmtree(cleaned_csv_path)

  # Get path to result file from configuration
  results = configuration.get('results_file', None)

  # Format results to uppercase, excluding set columns
  if file_type == 'ucas': csv_to_upper(results)
  if file_type == 'scl': csv_to_upper(results, exclude=['Fax number', 'Email address'])


def generate_clean_file(data: DataFrame, cleaned_file_name: str):
  """ Takes pandas data fram and creates a clean csv file. This prevents errors caused by unusual encodings. """

  if not os.path.exists(cleaned_csv_path):
      os.mkdir(cleaned_csv_path)

  data.to_csv(cleaned_csv_path + cleaned_file_name, index=False)
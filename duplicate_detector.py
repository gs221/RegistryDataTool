"""
DuplicateDetector.py

This file contains the functions that are used to identify suplicate schools in a single csv file. 

"""

import os
import csv_dedupe

from pandas import DataFrame
from csv_dedupe import csv_dedupe
from helpers import csv_to_upper, open_config_file, error

# Path for cleaned file to be stored 
cleaned_csv_path = './data/cleaned/'

def detect_duplicates(data: DataFrame, config_path: str) -> None:
  """ Detects duplicates in a singe csv file. """

  # Open and store configuration information from supplied file path. 
  configuration = open_config_file(config_path)

  # Get file type. This is used to distinguish between ucas and scl data. This allows for appropriate formatting. 
  file_type = configuration.get('file_type', None)

  if file_type == 'ucas': cleaned_file_name = 'ucas_for_option2.csv'
  elif file_type == 'scl': cleaned_file_name = 'scl_for_option3.csv'
  else: error('Malformed configuration file.')

  # Generate clean file from data for dedupe 
  generate_clean_file(data, cleaned_file_name)

  # Add input file path to configuration, this is used by csv_dedupe.py to determin the input filename. 
  configuration['input'] = cleaned_csv_path + cleaned_file_name

  # Find duplicates
  deduper = csv_dedupe.CsvDedupe(configuration)
  deduper.run()

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
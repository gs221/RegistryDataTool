"""
DuplicateDetector.py

This file contains the functions that are used to identify duplicate schools in a single csv file.

"""

import os
import csv_dedupe

import pandas as pd
from pandas import DataFrame
from csv_dedupe import csv_dedupe
from helpers import get_delimiter, open_config_file, get_file_path, pre_clean

# Path for cleaned file to be stored 
cleaned_csv_path = './data/tmp/'


def detect_duplicates() -> None:
    """ Detects duplicates in a singe csv file. """

    # Open and store configuration information from user selection
    configuration = open_config_file(None)

    # Get folder path for file
    folder_path = configuration.get('folder_path')

    # Search in folder for file
    file_path = get_file_path(folder_path, 'Please put data in' + folder_path + 'folder. This folder must contain a single data file.')

    # Pre-clean data file to remove any unwanted characters that may cause issue 
    print()  # Menu Formatting only
    if configuration.get('pre_clean', True):
        pre_clean(file_path)

    # Get encoding used by file (specified in config, defaults to iso-8859-15)
    file_encoding = configuration.get('file_encoding', 'iso-8859-15')

    # Auto-detect delimiters being used in files
    file_delimiter = get_delimiter(file_path, enc=file_encoding)

    # Get number of columns to be considered for each dataset
    columns = configuration.get('number_of_columns', None)

    # Stores file contents present in ucas and scl folders into data frames
    data: DataFrame = pd.read_csv(file_path,
                                  sep=file_delimiter,
                                  dtype=str,                            # All column types set to string to prevent type errors.
                                  usecols=[i for i in range(columns)],  # Only import set number of columns
                                  keep_default_na=False,                # Prevents Pandas from filling empty cells with NaN.
                                  encoding=file_encoding)               # Prevents decoding error when importing the data.

    # Generate clean file from data for dedupe
    generate_clean_file(data, 'option_two_temp.csv')

    # Add input file path to configuration, this is used by csv_dedupe.py to determine the input filename.
    configuration['input'] = cleaned_csv_path + 'option_two_temp.csv'

    # Find duplicates
    deduper = csv_dedupe.CsvDedupe(configuration)
    deduper.run()


def generate_clean_file(data: DataFrame, cleaned_file_name: str):
    """ Takes pandas data frame and creates a clean csv file. This prevents errors caused by unusual encodings. """

    if not os.path.exists(cleaned_csv_path):
        os.mkdir(cleaned_csv_path)

    data.to_csv(cleaned_csv_path + cleaned_file_name, index=False)

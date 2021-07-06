"""
DuplicateDetector.py

This file contains the functions that are used to identify duplicate schools in a single csv file.

"""

import os
import csv_dedupe

import pandas as pd
from pandas import DataFrame
from csv_dedupe import csv_dedupe
from settings import DATA_PATH
from helpers import get_delimiter, get_encoding, open_config, get_file_path, pre_clean, info

# Path for cleaned file to be stored 
cleaned_csv_path = './data/tmp/'

def detect_duplicates() -> None:
    """ Detects duplicates in a singe csv file. """

    # Open and store configuration information from user selection 
    conf = open_config()

    # Show that configuration files have been loaded successfully.
    info('Configuration file loaded successfully.', pre='\n')

    # Get filepath of file 
    conf.path = get_file_path(DATA_PATH + conf.folder_name, 'Please put ' + conf.folder_name + ' data in ' + conf.folder_name + ' folder. This folder must contain a single data file.')

    # Detect encoding for file and update configuration
    conf.encoding = get_encoding(conf.path)

    # Pre-clean file as per configuration 
    if conf.pre_clean:
        pre_clean(conf.path, conf.encoding, conf.characters_to_clean)

    # Print blank line for menu formatting 
    print()

    # Auto-detect delimiter used in file
    file_delimiter = get_delimiter(conf.path, encoding=conf.encoding)

    # Stores file contents present in configured folders into data frames
    data: DataFrame = pd.read_csv(conf.path, 
                                  sep=file_delimiter,
                                  dtype=str,
                                  usecols=conf.columns,
                                  keep_default_na=False,
                                  encoding=conf.encoding) 

    # Generate clean file from data for dedupe
    generate_clean_file(data, 'option_two_temp.csv')

    # Find duplicates
    deduper = csv_dedupe.CsvDedupe(conf)
    deduper.run()

def omit() -> None:
    """ Detects duplicates in a singe csv file. """

    # Open and store configuration information from user selection
    configuration = open_config()

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

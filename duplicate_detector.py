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

    # Stores file contents present in configured folders into data frame
    data: DataFrame = pd.read_csv(conf.path, 
                                  sep=file_delimiter,
                                  dtype=str,                # All column types set to string to prevent type errors. 
                                  usecols=conf.columns,     # Only import number of columns specified in config. 
                                  keep_default_na=False,    # Prevents Pandas from filling empty cells with NaN.
                                  encoding=conf.encoding)   # Prevents decoding error when importing the data. 

    # Generate clean file from data for dedupe
    generate_clean_file(data, 'option_two_temp.csv')

    # Find duplicates
    deduper = csv_dedupe.CsvDedupe(conf)
    deduper.run()


def generate_clean_file(data: DataFrame, cleaned_file_name: str):
    """ Takes pandas data frame and creates a clean csv file. This prevents errors caused by unusual encodings. """

    if not os.path.exists(cleaned_csv_path):
        os.mkdir(cleaned_csv_path)

    data.to_csv(cleaned_csv_path + cleaned_file_name, index=False)

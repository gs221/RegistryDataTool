"""
Record Matcher:

Contains functions that match records across two delimited files.
"""

import os
import pandas as pd

from csv_dedupe import csv_link
from menu import SingleSelectionMenu
from pandas.core.frame import DataFrame
from settings import DATA_PATH, TEMP_PATH, SCL_COLUMNS, UCAS_COLUMNS
from helpers import get_delimiter, get_encoding, open_config, open_config, get_file_path, pre_clean, info, todo, error, warning


def match_records() -> None:
    """ Matches records accross two files. """

    # Ask user to select two configuration files from configuration folder.
    conf_a = open_config()
    conf_b = open_config()

    # Show that configuration files have been loaded successfully.
    info('Configuration files loaded successfully.', pre='\n')

    # Check that recall weights are the same, use conf_a recall weight if not: 
    if conf_a.recall_weight != conf_b.recall_weight:
        info('Configuration files have different recall weights. The program will use the recall weight specified in the first configuration file. (' + str(conf_a.recall_weight) + ')')

    # Check that same number of columns are being considered. 
    if len(conf_a.column_names) != len(conf_b.column_names):
        error('When comparing files, you must specify the same number of columns to be compared.\n' + 
              '\tThis can be solved by adding/removing \'columns_names\' in the respective configuration files\n' + 
              '\tsuch that both have the same number listed. ')

    # Get filepath for each file
    conf_a.path = get_file_path(DATA_PATH + conf_a.folder_name, 'Please put ' + conf_a.folder_name + ' data in ' + conf_a.folder_name + ' folder. This folder must contain a single data file.')
    conf_b.path = get_file_path(DATA_PATH + conf_b.folder_name, 'Please put ' + conf_b.folder_name + ' data in ' + conf_b.folder_name + ' folder. This folder must contain a single data file.')

    # Detect encoding for each file and update configurations 
    conf_a.encoding = get_encoding(conf_a.path)
    conf_b.encoding = get_encoding(conf_b.path)

    # Pre-clean files as per configuration 
    if conf_a.pre_clean:
        pre_clean(conf_a.path, conf_a.encoding, conf_a.characters_to_clean)
    
    if conf_b.pre_clean:
        pre_clean(conf_b.path, conf_b.encoding, conf_b.characters_to_clean)

    # Blank line for menu formatting 
    print()

    # Auto-detect delimiters being used in files
    file_a_delimiter = get_delimiter(conf_a.path, encoding=conf_a.encoding)
    file_b_delimiter = get_delimiter(conf_b.path, encoding=conf_b.encoding)

    # Stores file contents present in configured folders into data frames
    data_a: DataFrame = pd.read_csv(conf_a.path, 
                                    sep=file_a_delimiter,
                                    dtype=str,                  # All column types set to string to prevent type errors. 
                                    usecols=conf_a.columns,     # Only import number of columns specified in config.
                                    keep_default_na=False,      # Prevents pandas from filling empty cells with NaN.
                                    encoding=conf_a.encoding)   # Prevents decoding error when importing the data. 
    
    data_b: DataFrame = pd.read_csv(conf_b.path, 
                                    sep=file_b_delimiter,
                                    dtype=str,
                                    usecols=conf_b.columns,
                                    keep_default_na=False,
                                    encoding=conf_b.encoding) 

    # Prompt user to determine whether or not ucas and scl data is being used (or not)
    todo('Please select an option from the list below.', post='\n')

    matcher_menu = SingleSelectionMenu(options=["Find schools with internal ID that now have UCAS ID (Works with: SCL and UCAS data only)", 
                                                "Find matches between files (Works with: All data)"])

    selection = matcher_menu.show()

    # Continue based on user selection 
    if selection == 1: 
        (conf_a, conf_b) = generate_clean_files(data_a, conf_a, data_b, conf_b, format=True)
    elif selection == 2: 
        (conf_a, conf_b) = generate_clean_files(data_a, conf_a, data_b, conf_b, format=False)

    # Find Matches
    ## Creates instance of and runs the linker program with the given configuration
    linker = csv_link.CsvLink(conf_a, conf_b)
    linker.run()


def identify_data(data_a, conf_a, data_b, conf_b):
    """ Determines which data is scl and which is ucas """

    # If every column in the scl check columns are in data_a then we know that data_a is the scl data.
    if all(columns in data_a.columns for columns in SCL_COLUMNS):
        scl = data_a
        
        # Having identified the scl data, we must now ensure that data_b is in fact ucas data.
        if all(columns in data_b.columns for columns in UCAS_COLUMNS):
            ucas = data_b
            return (scl, conf_a, ucas, conf_b)

    # If every column in the scl check columns are in data_b then we know that data_b is the scl data. 
    elif all(columns in data_b.columns for columns in SCL_COLUMNS):
        scl = data_b

        # Having identified the scl data, we must not ensure that data_a is in fact the ucas data. 
        if all(columns in data_a.columns for columns in UCAS_COLUMNS):
            ucas = data_a
            return (scl, conf_b, ucas, conf_a)

    # Returned if scl/ucas data cannot be identified
    return None


def generate_clean_files(data_a, conf_a, data_b, conf_b, format=False) -> None:
    """ Takes data frame produced by pandas, extracts unnecessary records and exports clean csv files to be used by duplicate finder."""

    # Generate directory for pandas generated csv files
    if not os.path.exists(DATA_PATH + TEMP_PATH):
        os.mkdir(DATA_PATH + TEMP_PATH)

    # If the user has opted to find scohols with internal ID that now has UCAS ID
    if format:
        
        # Store result of data identification in variable so it can be used after conditional statement
        identified_data = identify_data(data_a, conf_a, data_b, conf_b)

        if identified_data != None:

            # Split tuple into individual data frames
            (scl, scl_conf, ucas, ucas_conf) = identified_data

            # Remove records from UCAS data where corresponding school with ID is already in scl data
            ucas = ucas[ucas['School'].isin(scl['School code']) == False]

            # Remove UCAS codes and other malformed codes leaving only internal codes
            # Useful Regular Expression Site: https://regex101.com/ 
            scl = scl[scl['School code'].str.contains(r'^[a-zA-Z]{2}\d{3,5}$', na=False)]

            # Generate clean files and place in directory
            # Index is set to false to prevent pandas from writing the ID's it has given to each row.
            scl.to_csv(DATA_PATH + TEMP_PATH + 'temp_a.csv', index=False)
            ucas.to_csv(DATA_PATH + TEMP_PATH + 'temp_b.csv', index=False)  

            return (scl_conf, ucas_conf)
        else:
            warning('Unable to detect ucas/scl data. Continuing as if generic files were used.', pre='\n', post='\n') 

    # Generate clean files and place in directory
    # Index is set to false to prevent pandas from writing the ID's it has given to each row.
    data_a.to_csv(DATA_PATH + TEMP_PATH + 'temp_a.csv', index=False)
    data_b.to_csv(DATA_PATH + TEMP_PATH + 'temp_b.csv', index=False)

    return (conf_a, conf_b)


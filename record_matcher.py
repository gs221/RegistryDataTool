"""
Record Matcher:

Contains functions that match records across two delimited files.

"""

from menu import SingleSelectionMenu
import os

import pandas as pd
from csv_dedupe import csv_link
from pandas.core.frame import DataFrame
from settings import DATA_PATH, TEMP_PATH
from helpers import csv_to_upper, get_delimiter, get_encoding, open_config, open_config, get_file_path, pre_clean, info, todo, error, warning


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
                                    dtype=str,
                                    usecols=conf_a.columns,
                                    keep_default_na=False,
                                    encoding=conf_a.encoding) 
    
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
        generate_clean_files(data_a, data_b, format=True)
    elif selection == 2: 
        generate_clean_files(data_a, data_b, format=False)

    # Find Matches
    # Creates instance of and runs the linker program with the given configuration
    linker = csv_link.CsvLink(conf_a, conf_b)
    linker.run()


def omit() -> None:

    # Get paths to results files from configuration
    potential_matches = configuration.get('matches_file')
    ucas_only = configuration.get('ucas_only_file')
    scl_only = configuration.get('scl_only_file')

    # Format results to uppercase, excluding set columns
    csv_to_upper(potential_matches, exclude=['Fax number', 'Email address'])
    csv_to_upper(scl_only, exclude=['Fax number', 'Email address'])
    csv_to_upper(ucas_only)

def identify_data(data_a: DataFrame, data_b: DataFrame):
    # Determine which data is scl and which is ucas
        if len(data_a.columns) < len(data_b.columns):
            # ucas left scl right 
            return (data_a, data_b)
        elif len(data_a.columns) > len(data_b.columns):
            # ucas left scl right 
            return (data_b, data_a)
        else: 
            error('Could not identify data. This would suggest that both files have an equal number of columns.\n' + 
                  '\tAt the point of making this program, the SCL data has considerably more columns than the UCAS data.')

def generate_clean_files(data_a: DataFrame, data_b: DataFrame, format=False) -> None:
    """ Takes data frame produced by pandas, extracts unnecessary records and exports clean csv files to be used by duplicate finder."""

    if format:
        try:
            (ucas, scl) = identify_data(data_a, data_b)

            # Remove records from UCAS data where corresponding school with ID is already in scl data
            ucas = ucas[ucas['School'].isin(scl['School code']) == False]

            # Remove UCAS codes and other malformed codes leaving only internal codes
            scl = scl[scl['School code'].str.contains(r'^[a-zA-Z]{2}\d{3,5}$', na=False)]

            # Generate directory for pandas generated csv files
            if not os.path.exists(DATA_PATH + TEMP_PATH):
                os.mkdir(DATA_PATH + TEMP_PATH)

            # Generate clean files and place in directory
            # Index is set to false to prevent pandas from writing the ID's it has given to each row.
            scl.to_csv(DATA_PATH + TEMP_PATH + 'temp_a.csv', index=False)   # TODO
            ucas.to_csv(DATA_PATH + TEMP_PATH + 'temp_b.csv', index=False)  # TODO

            return 
        except KeyError:
            warning('Unable to detect ucas/scl data. Continuing as if generic files were used.', pre='\n', post='\n') 

    # Generate directory for pandas generated csv files
    if not os.path.exists(DATA_PATH + TEMP_PATH):
        os.mkdir(DATA_PATH + TEMP_PATH)

    # Generate clean files and place in directory
    # Index is set to false to prevent pandas from writing the ID's it has given to each row.
    data_a.to_csv(DATA_PATH + TEMP_PATH + 'temp_a.csv', index=False)
    data_b.to_csv(DATA_PATH + TEMP_PATH + 'temp_b.csv', index=False)


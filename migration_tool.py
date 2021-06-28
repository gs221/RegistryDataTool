import glob
import os

import pandas as pd
from pandas import DataFrame
from detect_delimiter import detect
from colorama import init
from helpers import cleanup_and_exit, pre_clean, try_again, info, error, todo
from school_matcher import match_schools
from duplicate_detector import detect_duplicates

def run_menu() -> None:
    """ - Verifies that required folders and documents are available.
        - Cleans and imports documents as they are used by all menu options.
        - Displays options menu to allow user to select appropriate tool.
    """

    print('--------------- Registry UCAS-SCL Migration Tool ---------------')

    # Check that the data folder exists, if not create it
    check_data_folder_exists()

    # Get and store filepath for each file
    ucas_path = get_file_path('./data/ucas/', 'Please put ucas data in ucas folder.')
    scl_path = get_file_path('./data/scl/', 'Please put scl data in scl folder.')

    # Pre-clean both data files to remove any unwanted characters that may cause issue 
    print() # Menu Formatting only 
    pre_clean(ucas_path)
    pre_clean(scl_path)

    # Open and store each file using filepath
    ucas_file = open(ucas_path)
    scl_file = open(scl_path)

    # Auto-detect delimiters being used in files
    ucas_delimiter = detect(ucas_file.readline())
    internal_delimiter = detect(scl_file.readline())

    # Close open files as they are no longer required 
    ucas_file.close()
    scl_file.close()

    # Stores file contents present in ucas and scl folders into data frames
    ucas_data: DataFrame = pd.read_csv(ucas_path, sep=ucas_delimiter, dtype=str, usecols=[i for i in range(30)], keep_default_na=False)    
    scl_data: DataFrame = pd.read_csv(scl_path, sep=internal_delimiter, dtype=str, usecols=[i for i in range(80)], keep_default_na=False)

    # Menu options
    print('\n1. Find centres with internal ID that now have relevant UCAS ID. ~10min')
    print('2. Detect duplicate schools in UCAS data only. ~15min')
    print('3. Detect duplicates in SCL data only. ~15min')
    print('4. Exit')
    print()
    selection = input("Please enter selection number: ")
    print()

    if selection == '1': match_schools(ucas_data, scl_data, './configurations/option_one_config.json')
    elif selection == '2': detect_duplicates(ucas_data, './configurations/option_two_config.json')
    elif selection == '3': detect_duplicates(scl_data, './configurations/option_three_config.json')
    elif selection == '4': cleanup_and_exit()
    else: error('Invaild menu option selected', post='\n')


def check_data_folder_exists() -> None:
    """ Checks that data folder exists. If it doesnt exist it is created. """

    if not os.path.exists('./data'): 
        info('Couldn\'t find ./data folder. This will now be created.', pre='\n')
        os.mkdir('./data')

    if not os.path.exists('./data/ucas'):
        info('Couldn\'t find ./data/ucas folder. This will now be created.')
        os.mkdir('./data/ucas')

    if not os.path.exists('./data/scl'):
        info('Couldn\'t find ./data/scl folder. This will now be created.')
        os.mkdir('./data/scl')


def get_file_path(path: str, msg: str) -> list[str]:
    """ Gets filepath of the first and only file in a folder. User is prompted until the folder contains a single file. """

    while True:
        folder_contents = glob.glob(os.path.join(path, '*.*'))
        file_missing = len(folder_contents) < 1 or len(folder_contents) > 1

        if file_missing:
            todo(msg, pre='\n', post='\n')
            try_again()
        else:
            return folder_contents[0]


def main() -> None:
    """ The first function that is called in the program. """

    # initialise colorama 
    init(autoreset=True)

    try:
        run_menu()
    except ValueError as e:
        print(e)
    except ZeroDivisionError as e:
        error('An attempt was made to divide by zero. This is likely casued by an attempt to proceed without training the program.')

    # Clean up before quitting
    cleanup_and_exit()


# Executes main
if __name__ == "__main__":
    main()


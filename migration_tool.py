import glob
import os

import pandas as pd
from pandas import DataFrame
from detect_delimiter import detect
from helpers import pre_clean, try_again
from school_matcher import match_schools

def run_menu() -> None:
    """ - Verifies that required folders and documents are available.
        - Cleans and imports documents as they are used by all menu options.
        - Displays options menu to allow user to select appropriate tool.
    """

    print('------------- Registry UCAS-SCL Migration Tool -------------\n')

    # Check that the data folder exists, if not create it
    check_data_folder_exists()

    # Get and store filepath for each file
    ucas_path = get_file_path('./data/ucas/', '[TODO] Please put ucas data in ucas folder.\n')
    scl_path = get_file_path('./data/scl/', '[TODO] Please put scl data in scl folder.\n')

    # Pre-clean both data files to remove any unwanted characters that may cause issue 
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
    internal_data: DataFrame = pd.read_csv(scl_path, sep=internal_delimiter, dtype=str, usecols=[i for i in range(80)], keep_default_na=False)

    # Menu options
    print('\n1. Find centres with internal ID that now have relevant UCAS ID.')
    print()
    selection = input("Please enter selection number: ")
    print()

    if selection == '1':
        match_schools(ucas_data, internal_data)
    else:
        print('[ERROR] Please run again and select a valid option (1)')


def check_data_folder_exists() -> None:
    """ Checks that data folder exists. If it doesnt exist it is created. """

    if not os.path.exists('./data'):
        print('[INFO] The following folders couldnt be found:\n\t- ./data\n\t- ./data/ucas\n\t- ./data/scl\n\t- ./data/training\nThey will now be created. ', end='')
        os.mkdir('./data')
        os.mkdir('./data/ucas')
        os.mkdir('./data/scl')
        os.mkdir('./data/training')
        print('(Finished)\n')


def get_file_path(path: str, err_msg: str) -> list[str]:
    """ Gets filepath of the first and only file in a folder. User is prompted until the folder contains a single file. """

    while True:
        folder_contents = glob.glob(os.path.join(path, '*.*'))
        file_missing = len(folder_contents) < 1 or len(folder_contents) > 1

        if file_missing:
            print(err_msg)
            try_again()
        else:
            return folder_contents[0]


def main() -> None:
    """ The first function that is called in the program. """

    try:
        run_menu()
    except ValueError as e:
        print(e)

# Executes main
if __name__ == "__main__":
    main()


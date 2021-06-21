import glob
import os

import pandas as pd
from pandas import DataFrame
from detect_delimiter import detect
from CentreSearch import centre_search
from FileCleaning import pre_clean

# Main Function
def main():
    try:
        run_menu()
    except FileNotFoundError as e:
        print(e)


def run_menu():
    print('------------- Registry UCAS-SCL Migration Tool -------------\n')

    # Ensure that data/ucas and data/scl exist 
    if not os.path.exists('./data'):
        print('[ERROR] The following folders do not exist:\n\t- ./data\n\t- ./data/ucas\n\t- ./data/scl\n\t- ./data/training\nThey will now be created. ', end='')
        os.mkdir('./data')
        os.mkdir('./data/ucas')
        os.mkdir('./data/scl')
        os.mkdir('./data/training')
        print('(Finished)\n')
        exit(0)

    # Gets filenames and paths of UCAS and SCL documents
    ucas_folder_contents = glob.glob(os.path.join('./data/ucas/', '*.*'))
    scl_folder_contents = glob.glob(os.path.join('./data/scl/', '*.*'))

    # Esure that Each folder contains a single data file
    ucas_missing = len(ucas_folder_contents) < 1 or len(ucas_folder_contents) > 1
    scl_missing = len(scl_folder_contents) < 1 or len(scl_folder_contents) > 1

    if ucas_missing and scl_missing:
        print("[ERROR] Please add SCL and UCAS data to the appropriate folders.\n")
        exit(0)

    if ucas_missing:
        print("[ERROR] Please ensure that UCAS folder contains a single data file.\n")
        exit(0)

    if scl_missing:
        print("[ERROR] Please ensure that SCL folder contains a single data file.\n")
        exit(0)

    # Store filepath for each file
    ucas_path = ucas_folder_contents[0]
    internal_path = scl_folder_contents[0]

    # Pre-clean both data files to remove any unwanted characters that may cause issue 
    pre_clean(ucas_path)
    pre_clean(internal_path)

    # Open and store each file using filepath
    ucas_file = open(ucas_path)
    internal_file = open(internal_path)

    # Auto-detect delimiters being used in files
    ucas_delimiter = detect(ucas_file.readline())
    internal_delimiter = detect(internal_file.readline())

    # Stores file contents present in ucas and internal folders into data frames
    ucas_data: DataFrame = pd.read_csv(ucas_path, sep=ucas_delimiter, dtype=str, usecols=[i for i in range(30)], keep_default_na=False)    
    internal_data: DataFrame = pd.read_csv(internal_path, sep=internal_delimiter, dtype=str, usecols=[i for i in range(80)], keep_default_na=False)

    print('\n1. Find centres with internal ID that now have relevant UCAS ID.')
    print()

    selection = input("Please enter selection number: ")

    print()

    if selection == '1':
        centre_search(ucas_data, internal_data)
    else:
        print('[ERROR] Please run again and select a valid option (1)')


# Executes Main Function
if __name__ == "__main__":
    main()

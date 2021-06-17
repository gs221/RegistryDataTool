import argparse
import glob
import os
from sys import intern

import pandas as pd
from pandas import DataFrame
from detect_delimiter import detect
from CentreSearch import centre_search
from PreClean import pre_clean

# Main Function
def main():
    try:
        run_menu()
    except FileNotFoundError as e:
        print(e)


def run_menu():
    print('------------- Registry UCAS-SCL Migration Tool -------------\n')

    # Gets filenames and paths of UCAS and SCL documents
    ucas_folder_contents = glob.glob(os.path.join('./Data/ucas/', '*.*'))
    internal_folder_contents = glob.glob(os.path.join('./Data/internal/', '*.*'))

    # Esure that Each folder contains a single data file
    if len(ucas_folder_contents) < 1 or len(ucas_folder_contents) > 1:
        print("[ERROR] Please ensure that UCAS folder contains a single data file")
        exit(0)

    if len(internal_folder_contents) < 1 or len(internal_folder_contents) > 1:
        print("[ERROR] Please ensure that Internal folder contains a single data file")
        exit(0)

    # Store filepath for each file
    ucas_path = ucas_folder_contents[0]
    internal_path = internal_folder_contents[0]

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

    selection = input("Please enter selection: ")
    #selection = '1'

    print('\n')

    if selection == '1':
        centre_search(ucas_data, internal_data)
    else:
        print('[ERROR] Please run again and select a valid option (1)')


# Executes Main Function
if __name__ == "__main__":
    main()

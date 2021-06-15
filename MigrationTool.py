import argparse
import glob
import os

import pandas as pd
from pandas import DataFrame
from detect_delimiter import detect
from tabulate import tabulate

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

    # Open and store each file using filepath
    ucas_file = open(ucas_path)
    internal_file = open(internal_path)

    # Auto-detect delimiters being used in files
    ucas_delimiter = detect(ucas_file.readline())
    internal_delimiter = detect(internal_file.readline())

    # Stores file contents present in ucas and internal folders into data frames
    ucas_data: DataFrame = pd.read_csv(ucas_path, sep=ucas_delimiter, dtype=str, usecols=[i for i in range(31)])
    internal_data: DataFrame = pd.read_csv(internal_path, sep=internal_delimiter, dtype=str, usecols=[i for i in range(80)])

    print('1. Find centres now using UCAS code')
    print()

    selection = input("Please enter selection: ")

    print('\n')

    if selection == '1':
        print_headers(ucas_data, internal_data)
    else:
        print('[ERROR] Please run again and select a valid option (1-3)')


# Takes heading from each column of given files and prints valid headers
def print_headers(ucas: DataFrame, internal: DataFrame):
    print('------ UCAS Columns ------', *ucas.columns, sep = "\n")
    print('\n------ Internal ------', *internal.columns, sep = "\n")


# Validates comparison file 

# Searches for centres that now use UCAS code 
def centre_search(ucas: DataFrame, internal: DataFrame):
    print()

def existing_removed(ucas: DataFrame, internal: DataFrame):
    for ucas_school in ucas['School']:
        for internal_school in internal['School code']:
            if ucas_school == internal_school:
                print('woop')
            ucas.drop(df[df.score < 50].index, inplace=True)
    #ucas[internal['School code'] == ucas['School']]

# Executes Main Function
if __name__ == "__main__":
    main()

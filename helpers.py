"""
File Helpers: 

Contains helpful functions that are frequently used across multiple files. 
"""

import os
import sys
import json
import glob
import shutil

import pandas as pd
from colorama import Fore
from platform import system
from pandas import DataFrame
from detect_delimiter import detect
from menu import SingleSelectionMenu
from colorama.initialise import deinit
from json.decoder import JSONDecodeError


def pre_clean(f):
    """ Removes any quotation marks from the files to prevent errors during importation. """

    info('Pre-Cleaning ' + f.split('/')[-1], fin='')  # Prints info message and gets filename from file path.

    with open(f, 'r', encoding='iso-8859-15') as file:  # Opens file with appropriate encoding (for read)
        f_cleaned = file.read().replace('"', '')  # Replaces all quotation marks with nothing

    with open(f, 'w', encoding='iso-8859-15') as file:  # Opens file with appropriate encoding (for write)
        file.write(f_cleaned)  # Writes cleaned file to file

    print(' (Finished)')


def open_config_file(default_config: str, path='./configurations/') -> dict:
    """ Attempts to open and parse the supplied configuration file. Returns dictionary containing configuration. """

    try:
        if default_config is not None and os.path.exists(path + default_config):
            # Tries to read and parse default configuration file from given path.
            with open(path + default_config, 'r') as config_file:
                return json.load(config_file)
        else:
            # Otherwise informs the user that default config file could not be found.
            info('Please select a configuration file from the list below.', pre='\n', post='\n')

            # Gets a list of .config files in path 
            config_files = glob.glob(os.path.join(path, '*.config'))

            # If there is less than one configuration file in the path, print error. 
            if len(config_files) < 1: 
                error('Couldnt find any configuration files. Ensure they are in the configuration folder and have extension .config.')

            # Generates menu consisting of discovered config files.
            config_menu = SingleSelectionMenu(options=config_files)

            # Attempts to parse and return user selected configuration 
            # -1 as list index starts at 0 but menu selections start at 1. 
            with open(config_files[config_menu.show() - 1], 'r') as config_file:
                return json.load(config_file)

    except FileNotFoundError:
        # If the file could not be found, print  meaningful error message.
        error('Could not find configuration file.')

    except JSONDecodeError:
        # if the file could not be parsed (contains invalid JSON) then print error message.
        error('Could not parse selected configuration file. Please ensure it contains only valid JSON.')


def try_again() -> None:
    """ Prompts the user to retry some process or exit program """

    while True:
        value = input("Enter 't' to try again or 'e' to exit. ").lower()
        if value == 't': return
        if value == 'e': sys.exit(0)


def csv_to_upper(file_path: str, exclude=[]) -> None:
    """ Converts every column to uppercase in given file excluding column names set to exclude. """

    # Check that file exists
    if not os.path.isfile(file_path):
        error('Could not locate \'' + file_path + '\'. Formatting could not be performed.')

    # Print informative message to user
    info('Formatting ' + file_path + '.', fin='')

    # If columns have been given to exclude from formatting, print columns
    if exclude:
        print(' Excluding columns: ', end='')
        print(*exclude, sep=', ', end='')
        print('.', end='')

    # Import file into pandas
    file_data: DataFrame = pd.read_csv(file_path, sep=',', dtype=str, keep_default_na=False)

    # Make all columns uppercase in all files
    file_data = file_data.apply(lambda x: x.str.upper())

    # Convert excluded columns back to lowercase
    for column in exclude:
        file_data[column] = file_data[column].str.lower()

    # Write formatted tables to file
    file_data.to_csv(file_path, index=False)

    print(' (Finished)')


def error(msg: str, fin=None, pre='', post='') -> None:
    """ Prints supplied error message and sys.exits(1) """
    print(coloured(pre + '[ERROR] ', Fore.RED) + msg + post, end=fin)
    cleanup_and_exit()


def todo(msg: str, fin=None, pre='', post='') -> None:
    """ Prints supplied todo message. """
    print(pre + coloured('[TODO] ', Fore.YELLOW) + msg + post, end=fin)


def info(msg: str, fin=None, pre='', post='') -> None:
    """ Prints supplied info message. """
    print(pre + coloured('[INFO] ', Fore.GREEN) + msg + post, end=fin)


def coloured(string: str, colour) -> str:
    """ returns string with colour information surrounding. """
    return colour + string + Fore.RESET


def cleanup_and_exit(prompt=True) -> None:
    """ Cleans stuff before exiting. """

    # Disarm colorama
    deinit()

    # Remove temporary directories
    if os.path.exists('./data/training'): shutil.rmtree('./data/training')
    if os.path.exists('./data/tmp'): shutil.rmtree('./data/tmp')

    # Exit program
    if prompt: input('Press enter to exit ')
    sys.exit(0)


def time_estimate(win='', other='', all='') -> str:
    """ Returns string time estimate based on current operating system. win(dows) or otherwise. """

    # If all is set reurn estimate regardless of system type.
    if all != '': return '~' + all + 'min'

    # If system is windows, return estimate for windows only. 
    if system() == 'Windows': return '~' + win + 'min'

    # Otherwise return estimate for other system types. 
    return '~' + other + 'min'


def get_file_path(path: str, msg: str) -> str:
    """ Gets filepath of the first and only file in a folder. User is prompted until the folder contains a single file. """

    while True:
        folder_contents = glob.glob(os.path.join(path, '*.*'))                  # Searches for any file name * with any extension * in the given path.
        file_missing = len(folder_contents) < 1 or len(folder_contents) > 1     # True when folder contains single file. False otherwise.

        if file_missing:                    # If the file is missing (or there is more than one file)
            todo(msg, pre='\n', post='\n')  # Print todo message to prompt user to insert file into folder.
            try_again()                     # Gets user to enter 't' to try again, or 'e' to exit the program.
        else:
            return folder_contents[0]       # [0] refers to first element of list of folder contents. This is the path to the one and only file in the folder.

def get_delimiter(file_path:str, enc=None) -> str:
    """ Opens, reads and closes a file automatically detecting the delimiter being used. """

    if enc is not None:
        with open(file_path, encoding=enc) as file:
            return detect(file.readline())
    else:
        with open(file_path) as file:
            return detect(file.readline())
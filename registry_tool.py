"""
Registry Tool: 

This file creates the data folder (if it doesnt already exist), loads the main menu and calls respective options 
based on user input. Contains overall exception handling. 
"""

import os

import colorama
from link_checker import check_links
from menu import SingleSelectionMenu
from record_matcher import match_records
from configuration_manager import DATA_PATH
from duplicate_detector import detect_duplicates
from helpers import cleanup_and_exit, info, error
from difference_detector import detect_differences


def run_menu() -> None:
    """ - Verifies that required folders and documents are available.
        - Cleans and imports documents as they are used by all menu options.
        - Displays options menu to allow user to select appropriate tool.
    """
    
    print('---------------- Registry Data Tool ----------------')

    # Check that the data folder exists, if not creates it. Should you wish to change the data folder name or path,
    # go to the configuration_manager.py file and modify the DATA_PATH variable.
    if not os.path.exists(DATA_PATH):
        info('Couldn\'t find ' + DATA_PATH + ' folder. This will now be created.', pre='\n')
        os.mkdir(DATA_PATH)

    # Sets menu options, each item in list will become numbered menu option 
    menu_options = ['Match records between two files.',
                    'Detect duplicates within a single file.',
                    'Verify links in file.',
                    'Check for differences between records with same ID accross two files.',
                    'Exit']

    # Create menu with above menu options
    main_menu = SingleSelectionMenu(options=menu_options)

    # Menu formatting only (blank line)
    print()

    # Show menu options and get user selection 
    selection = main_menu.show()

    # Run operation based on user selection 
    if selection == 1: 
        match_records()
    elif selection == 2: 
        detect_duplicates()
    elif selection == 3: 
        check_links()
    elif selection == 4: 
        detect_differences()
    elif selection == 5:
        cleanup_and_exit(prompt=False)
    else: error('Invalid menu option selected', post='\n', pre='\n')


def main() -> None:
    """ The first function that is called in the program. """

    # Initialise colorama, this facilitates [INFO] and [ERROR] messages being different colours. 
    colorama.init(autoreset=True)

    try:
        # Attempt to run program menu. 
        run_menu()

    except ZeroDivisionError as e:
        # If zero division error is raised, catch it and print error message. 
        # If this happens it is likely caused by an attempt to skip training (entering finish immediately when training)
        error('An attempt was made to divide by zero. This is likely caused by an attempt to proceed without training the program.')

    # except Exception as e:
    #     # If all else fails, print exception. 
    #     error(str(e))

    # Clean up before quitting
    cleanup_and_exit()


# Executes main method
if __name__ == "__main__":
    main()


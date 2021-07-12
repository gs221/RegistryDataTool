
import os

from colorama import init
from link_checker import check_links
from record_matcher import match_records
from configuration_manager import DATA_PATH, Configuration
from duplicate_detector import detect_duplicates
from helpers import cleanup_and_exit, info, error, time_estimate


def run_menu() -> None:
    """ - Verifies that required folders and documents are available.
        - Cleans and imports documents as they are used by all menu options.
        - Displays options menu to allow user to select appropriate tool.
    """
    
    print('---------------- Registry Data Tool ----------------\n')

    # Check that the data folder exists, if not creates it. Should you wish to change the data folder name or path,
    # go to the configuration_manager.py file and modify the DATA_PATH variable.
    if not os.path.exists(DATA_PATH):
        info('Couldn\'t find ' + DATA_PATH + ' folder. This will now be created.')
        os.mkdir(DATA_PATH)
        print() # Menu formatting only 

    # Menu options
    print('1. Match records between two files           ' + time_estimate(windows='10', other_os='20'))
    print('2. Detect duplicates within a single file    ' + time_estimate(windows='60', other_os='15'))
    print('3. Verify links in file                      ' + time_estimate(all_os='60'))
    print('4. Exit')
    print()
    selection = input("Please enter selection [1-4]: ")

    # Run operation based on user selection 
    if selection == '1': 
        match_records()
    elif selection == '2': 
        detect_duplicates()
    elif selection == '3': 
        check_links()
    elif selection == '4': 
        cleanup_and_exit(prompt=False)
    else: error('Invalid menu option selected', post='\n', pre='\n')


def main() -> None:
    """ The first function that is called in the program. """

    # Initialise colorama, this facilitates [INFO] and [ERROR] messages being different colours. 
    init(autoreset=True)

    try:
        # Attempt to run program menu. 
        run_menu()

    except ValueError as e:
        # If value error is raised, catch it and print error message. 
        error(str(e))

    except TypeError as e: 
        error(str(e))

    except ZeroDivisionError as e:
        # If zero division error is raised, catch it and print error message. 
        # If this happens it is likely caused by an attempt to skip training (entering finish immediately)
        error('An attempt was made to divide by zero. This is likely caused by an attempt to proceed without training the program.')

    except Exception as e:
        # If all else fails, print exception. 
        error(e)

    # Clean up before quitting
    cleanup_and_exit()


# Executes main method
if __name__ == "__main__":
    main()


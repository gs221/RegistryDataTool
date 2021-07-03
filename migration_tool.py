import os

from colorama import init
from link_checker import check_links
from school_matcher import match_schools
from duplicate_detector import detect_duplicates
from helpers import cleanup_and_exit, info, error, time_estimate


def run_menu() -> None:
    """ - Verifies that required folders and documents are available.
        - Cleans and imports documents as they are used by all menu options.
        - Displays options menu to allow user to select appropriate tool.
    """

    print('-------------------------- Registry Data Tool --------------------------\n')

    # Check that the data folders exist, if not create them. 
    check_data_folders()

    # Menu options
    print('1. Find centres with internal ID that now have relevant UCAS ID. ' + time_estimate(windows='10', other_os='20'))
    print('2. Detect duplicates within a single file. ' + time_estimate(windows='15', other_os='60'))
    print('3. Verify links in Org data. ' + time_estimate(all_os='1'))
    print('4. Exit')
    print()
    selection = input("Please enter selection [1-4]: ")

    # Run operation based on user selection 
    if selection == '1': match_schools()
    elif selection == '2': detect_duplicates()
    elif selection == '3': check_links()
    elif selection == '4': cleanup_and_exit(prompt=False)
    else: error('Invalid menu option selected', post='\n')


def check_data_folders() -> None:
    """ Checks that data folder exists. If it doesnt exist it is created. """

    print_line = False

    if check_folder('./data'): print_line = True; 
    if check_folder('./data/ucas'): print_line = True; 
    if check_folder('./data/scl'): print_line = True; 
    if check_folder('./data/org'): print_line = True; 
    
    if print_line: print()


def check_folder(path: str) -> bool:
    """ Checks that a given path exists. If it doesnt, prints info and makes path. """
    
    if not os.path.exists(path):
        info('Couldn\'t find ' + path + ' folder. This will now be created.')
        os.mkdir(path)
        return True

    return False


def main() -> None:
    """ The first function that is called in the program. """

    # Initialise colorama, this facilitates [INFO] and [ERROR] messages being different colours. 
    init(autoreset=True)

    try:
        # Attempt to run program menu. 
        run_menu()

    except ValueError as e:
        # If value error is raised, catch it and print error message. 
        print(e)

    except TypeError: 
        error('Invalid configuration selected.')

    except ZeroDivisionError as e:
        # If zero division error is raised, catch it and print error message. 
        # If this happens it is likely caused by an attempt to skip training (entering finish immediately)
        error('An attempt was made to divide by zero. This is likely caused by an attempt to proceed without training the program.')

    except Exception:
        # If all else fails, print exception. 
        error('An unexpected error occurred.', post='\n')

    # Clean up before quitting
    cleanup_and_exit()


# Executes main method
if __name__ == "__main__":
    main()


class SingleSelectionMenu:
    """ Contains options to allow a menu to be created from which a single option can be selected. """

    def __init__(self, title=None, options=None) -> None:
        """ Inintialises menu with optional title and options. These can be added here or with the respective functions. """
        self.title = title
        
        if options == None:
            self.options = []
        else:
            self.options = options

    def add_title(self, title: str) -> None:
        """ Sets or adds menu title. """
        self.title = title

    def add_option(self, option: str) -> None:
        """ Appends option to list of options. """
        self.options.append(option)

    def show(self, run_before=None) -> int:
        """ Shows the menu as configured. Returns validated value entered by user. """

        # If there are no options for menu and attempt is made to show menu, show error. 
        from helpers import error
        if len(self.options) < 1: 
            error('Menu must have at least one option.')

        # Print menu title if one exists.
        if self.title is not None: 
            print(self.title)

        # Run run_before function if one is given 
        if run_before is not None: 
            run_before()

        # Print menu options with number next to each.
        for number, option in enumerate(self.options, 1):
            print(str(number) + '. ' + option)

        # Spacing between options and user prompt 
        print()

        # Repeatedly ask user to select option from menu until valid selection is made.
        while True: 
            # Print selection prompt with spacing.
            selection = input('Please enter selection [1-' + str(len(self.options)) + ']: ')

            # Attempts to check if users option is valid. 
            try: 
                # If the users selection is an integer in the range consisting of the number of menu options.
                if int(selection) in range(1, len(self.options) + 1):
                    # Return the users selection.
                    return int(selection) 
                else:
                    # Otherwise raise exception as user input was invalid.
                    raise ValueError

            # Catches cases where user enters invalid integer or string, which cannot be parsed to a number.
            except ValueError:
                pass


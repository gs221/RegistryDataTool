"""
Configuration Manager: 

Contains class that loads and performs preliminary validation on configuration files. 
"""

import os
import yaml

from settings import DATA_PATH

class Configuration():
    def __init__(self, yml_path: str) -> None:
        from helpers import error

        # Attempt to open and load configuration file.
        with open(yml_path, 'r') as config:
            try:
                self.conf = yaml.safe_load(config)
            except yaml.YAMLError as e:
                error('Malformed configuration file. Please ensure the file contains only valid YAML.\n\n',
                      post=str(e) + '\n\nFor additional help see yaml documentation: https://bit.ly/3wiDdT6')

        # Store contents of configuration file.
        self.folder_name = self.__load('folder_name')
        self.column_count = self.__load('column_count', can_be_blank=True)
        self.pre_clean = self.__load('pre_clean')
        self.characters_to_clean = self.__load('characters_to_clean', can_be_blank=True)
        self.column_names = self.__load('column_names')
        self.recall_weight = self.__load('recall_weight')
        self.url_columns = self.__load('url_columns', can_be_blank=True)
        self.id_column = self.__load('id_column', can_be_blank=True)
        self.diff_columns = self.__load('diff_columns', can_be_blank=True)
    
        # Perform additional validation on configuration 
        self.__additional_validation()

        # Generate columns list
        if self.column_count is None:
            self.columns = None
        else: 
            self.columns = [i for i in range(self.column_count)]

        # Create file folder in data folder if it doesnt already exist
        if not os.path.exists(DATA_PATH + str(self.folder_name)):
            os.mkdir(DATA_PATH + str(self.folder_name))


    def __load(self, yaml_name: str, can_be_blank=False):
        """ Ensures that options are not left blank, returns value. """

        from helpers import error

        try:

            # If the value of the given option is none (empty/blank) and the value cannot be left blank,
            if self.conf.get(yaml_name) is None and can_be_blank is False:
                # Print error and exit.
                error('The option \'' + yaml_name + '\' cannot be left blank.')
            else:
                # Return value
                return self.conf.get(yaml_name, None)

        except AttributeError:
            error('Malformed configuration file. Please ensure the file contains only valid YAML.' +
                  '\n\tFor additional help see yaml documentation: https://bit.ly/3wiDdT6')


    def __additional_validation(self):
        """ Performs additional validation on configuration options. Ensures that types and values are as expected. """

        from helpers import error

        if self.column_count is not None:
            # Column count must be an integer (whole number)
            if not isinstance(self.column_count, int):
                error('Column count must be an whole number value, \'' + str(self.column_count) + '\' is invalid.')

            # Column count must be a number greater than 0
            if self.column_count < 1:
                error('Column count cannot be ' + str(self.column_count) + '. ')

        # Pre clean must be yes or no (true/false)s
        if not isinstance(self.pre_clean, bool): 
            error('Pre clean must be either yes or no. \'' + str(self.pre_clean) + '\' is invalid.')
        
        # If no characters are given to clean, set pre_clean to false. 
        if self.characters_to_clean == None or self.characters_to_clean == [None]:
            self.pre_clean = False

        # Ensure that there is at least one column name 
        if self.column_names == None or self.column_names == [None]:
            error('At least one column name has to be specified. ')

        # Ensure that recall weight is whole or decimal number 
        if not (isinstance(self.recall_weight, int) or isinstance(self.recall_weight, float)):
            error('Recall weight must be a number. \'' + str(self.recall_weight) + '\' is invalid.')

        # Ensure recall weight is greater than zero 
        if self.recall_weight < 1:
            error('Recall weight must be greater than zero.')

        # Ensure that url columns is list if single column given by user
        if not isinstance(self.url_columns, list):
            self.url_columns = [self.url_columns]
        
        # Ensure that diff columns is list if single column given by user
        if not isinstance(self.diff_columns, list):
            self.diff_columns = [self.diff_columns]

            
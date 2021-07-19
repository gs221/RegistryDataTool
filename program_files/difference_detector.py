""" 
Difference Detector: 

Detects changes across two delimited files. For example, could check if the status flags have changed 
beween ucas and scl data. 
"""

import pandas as pd
from pandas import DataFrame

from program_files.settings import DATA_PATH, DIFFERENCES, OUTPUT_PATH
from program_files.helpers import open_config, info, get_file_path, get_encoding, pre_clean, get_delimiter, error

def detect_differences():
  """ Detects differences between rows with the same ID (across two files) """

# Ask user to select two configuration files from configuration folder.
  conf_a = open_config()
  conf_b = open_config()

  # Show that configuration files have been loaded successfully.
  info('Configuration files loaded successfully.', pre='\n')

  # Check that two different configurations were selected 
  if conf_a.config_path == conf_b.config_path:
      error('You selected the same configuration twice (' + conf_a.config_path + '). Select two different config files.')

  # If id column and url column(s) are not given this option cannot be run, exit. 
  if conf_a.id_column == None or conf_a.diff_columns == [None]:
    error('The first configuration file you selected is missing a unique \'id_column\' or one or more \'diff_column\'')

  if conf_b.id_column == None or conf_b.diff_columns == [None]:
    error('The second configuration file you selected is missing a unique \'id_column\' or one or more \'diff_column\'')

  # Check that same number of columns are being considered. 
  if len(conf_a.diff_columns) != len(conf_b.diff_columns):
      error('When searching for changes, you must specify the same number of columns to be compared.\n' + 
            '\tThis can be solved by adding/removing \'diff_columns\' in the respective configuration files\n' + 
            '\tsuch that both have the same number listed. ')

  # Get filepath for each file
  conf_a.path = get_file_path(DATA_PATH + conf_a.folder_name, 'Please put ' + conf_a.folder_name + ' data in ' + conf_a.folder_name + ' folder. This folder must contain a single data file.')
  conf_b.path = get_file_path(DATA_PATH + conf_b.folder_name, 'Please put ' + conf_b.folder_name + ' data in ' + conf_b.folder_name + ' folder. This folder must contain a single data file.')

  # Detect encoding for each file and update configurations 
  conf_a.encoding = get_encoding(conf_a.path)
  conf_b.encoding = get_encoding(conf_b.path)

  # Pre-clean files as per configuration 
  if conf_a.pre_clean:
      pre_clean(conf_a.path, conf_a.encoding, conf_a.characters_to_clean)
  
  if conf_b.pre_clean:
      pre_clean(conf_b.path, conf_b.encoding, conf_b.characters_to_clean)

  # Blank line for menu formatting 
  print()

  # Auto-detect delimiters being used in files
  file_a_delimiter = get_delimiter(conf_a.path, encoding=conf_a.encoding)
  file_b_delimiter = get_delimiter(conf_b.path, encoding=conf_b.encoding)

  # Stores file contents present in configured folders into data frames
  data_a: DataFrame = pd.read_csv(conf_a.path, 
                                  sep=file_a_delimiter,
                                  dtype=str,                  # All column types set to string to prevent type errors. 
                                  usecols=conf_a.columns,     # Only import number of columns specified in config.
                                  keep_default_na=False,      # Prevents pandas from filling empty cells with NaN.
                                  encoding=conf_a.encoding)   # Prevents decoding error when importing the data. 
  
  data_b: DataFrame = pd.read_csv(conf_b.path, 
                                  sep=file_b_delimiter,
                                  dtype=str,
                                  usecols=conf_b.columns,
                                  keep_default_na=False,
                                  encoding=conf_b.encoding) 

  # If specified columns in conf_a are not in data_a, exit. 
  for column in conf_a.diff_columns:
      if not column in data_a.columns:
          error('Could not find \'' + column + '\' column. Have you entered it correctly in the configuration file?')

  for column in conf_b.diff_columns:
      if not column in data_b.columns:
          error('Could not find \'' + column + '\' column. Have you entered it correctly in the configuration file?')


  # Remove uncommon records from data_a (Data does not have a shared id in data_b) and vice versa
  data_a_condensed = data_a[data_a[conf_a.id_column].isin(data_b[conf_b.id_column])].sort_values(conf_a.id_column)
  data_b_condensed = data_b[data_b[conf_b.id_column].isin(data_a[conf_a.id_column])].sort_values(conf_b.id_column)

  # When sorting by unique id, the index column is no longer sequential
  # This removes the current index column and adds a new index colum with values 0 - number of records. 
  data_a_index_reset = data_a_condensed.reset_index(drop=True)
  data_b_index_reset = data_b_condensed.reset_index(drop=True)

  # Combine columns from data_b to the right of data_a
  combined = pd.concat([data_a_index_reset, data_b_index_reset], axis=1)

  for a_column, b_column in zip(conf_a.diff_columns, conf_b.diff_columns):
    diff = combined.loc[combined[a_column].ne(combined[b_column])]
    combined.drop(diff.index, inplace=True)

  # Save differences to csv
  diff.to_csv(OUTPUT_PATH + DIFFERENCES, index=False)

  # Info message for user
  info('Complete! Results saved to ' + OUTPUT_PATH + DIFFERENCES)
  
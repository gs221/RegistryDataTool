from settings import DATA_PATH
from requests.api import head
from os import sep
import pandas as pd
from pandas import DataFrame
import requests
import re
import validators
from threading import Thread
import csv
from helpers import info, open_config, pre_clean, get_file_path, get_delimiter, get_encoding, error
import grequests
import itertools

def check_links():
    # Get file configuration 
    conf = open_config()

    # Show that configuration files have been loaded successfully.
    info('Configuration file loaded successfully.', pre='\n')

    # Get filepath of file 
    conf.path = get_file_path(DATA_PATH + conf.folder_name, 'Please put ' + conf.folder_name + ' data in ' + conf.folder_name + ' folder. This folder must contain a single data file.')

    # Detect encoding for file and update configuration
    conf.encoding = get_encoding(conf.path)

    # Pre-clean file as per configuration 
    if conf.pre_clean:
        pre_clean(conf.path, conf.encoding, conf.characters_to_clean)

    # Print blank line for menu formatting 
    print()

    # Auto-detect delimiter used in file
    file_delimiter = get_delimiter(conf.path, encoding=conf.encoding)

    # Stores file contents present in configured folders into data frame
    data: DataFrame = pd.read_csv(conf.path, 
                                  sep=file_delimiter,
                                  dtype=str,
                                  usecols=conf.columns,
                                  keep_default_na=False,
                                  encoding=conf.encoding) 

    # If no column has been specified in config, exit. 
    if conf.url_column is None:
        error('No url_column specified in selected configuration.')

    # If specified column is not in data, exit. 
    if not conf.url_column in data.columns:
        error('Could not find ' + conf.url_column + '. Have you entered it correctly in the configuration file?')

    # Add additional column to start of data to show result of link checking 
    data.insert(loc=data.columns.get_loc(conf.url_column), column='Link check', value='')

    # Get list of links 
    links = data[conf.url_column].tolist()

    # Pre-proccess links




    # for i in range(len(links)):
    #     # Convert to lower case and remove leading and trailing whitespace
    #     links[i] = links[i].lower().strip()

    #     # Regular expressions used to find matching strings/sub-strings
    #     whitespace = re.compile(r'^\s*$')
    #     valid_characters = re.compile(r"^[:\/?#[\]@!$&'()*+,;=\w\-~.%]+$")   # According to RFC3986 sections 2.4 and 2.5

    #     # If link is whitespace then set to empty
    #     if whitespace.match(links[i]):
    #         links[i] = 'EMPTY'
    #         continue

    #     # If link has invalid characters
    #     elif not valid_characters.match(links[i]):
    #         links[i] = 'INVALID'
    #         continue

    #     else:
    #         links[i] = 'UNCHECKED'



    data['Link check'] = links

    data.to_csv('links_checked.csv', index=False)


def format_link(link: str) -> str:
    # Convert to lower case and remove leading and trailing whitespace
    link = link.lower().strip()

    # If link is empty then return 
    if link == '': return ''

    # remove https and http from start
    link = re.sub('https{0,1}(:|;)\/\/', '', link)

    return link

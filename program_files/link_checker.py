"""
Link Checker: 

Automatically tests links in a file. 
"""

import re
import json
import requests
import pandas as pd
import concurrent.futures

from pandas import DataFrame
from requests.models import Response
from json.decoder import JSONDecodeError
from program_files.helpers import info, open_config, pre_clean, get_file_path, get_delimiter, get_encoding, error
from program_files.settings import DATA_PATH, EMPTY, NO_RESPONSE, REQUEST_TIMEOUT, VERIFY_CERT, WAYBACK_MACHINE, WBM_API, USE_WBM, LINKS_CHECKED, OUTPUT_PATH

# Disable insecure request warning, caused by setitng verify=False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set Warnings 
import logging 
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.ERROR)


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
    if conf.url_columns == None or conf.url_columns == [None]:
        error('No url_column(s) specified in selected configuration.')

    # If specified column is not in data, exit. 
    for column in conf.url_columns:
        if not column in data.columns:
            error('Could not find ' + column + '. Have you entered it correctly in the configuration file?')

    # Tell user that link checking has started. 
    info('Link checking has started, this may take a while. (~2min per 1k urls)')

    # Validate links in all url column
    for count, column in enumerate(conf.url_columns, 1):

        # Add additional column(s) to data to show result of link checking 
        data.insert(loc=data.columns.get_loc(column), column='Link Check-' + str(count), value='')

        # Get list of links 
        links = data[column].tolist()

        # Format links (remove http, https, blank spaces)
        formatted_links = format_links(links)

        # Run requests concurrently and get responses
        responses = run_requests(formatted_links)

        # Create dictionary from original list of links
        links_dict = dict(enumerate(formatted_links))

        # If there are as many formatted links as there are responses (there should always be)
        if len(formatted_links) == len(responses):
            # for every link 
            for k in links_dict.keys():
                # Put response codes in correct position 
                links_dict[k] = responses[k].status_code if isinstance(responses[k], Response) else responses[k]
        else:
            error('The number of responses differs from the number of original requests.')

        # Add responses to link check column 
        data['Link Check-' + str(count)] = links_dict.values()


    # Write new data to file 
    data.to_csv(OUTPUT_PATH + LINKS_CHECKED, index=False)

    # Info message for user
    info('Complete! Results saved to ' + OUTPUT_PATH + LINKS_CHECKED)


def run_requests(links):
    """ Executes the lists of requests concurrently and returns responses (not in order). """

    # Empty list to store responses 
    responses = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as exec:
        future_to_url = {exec.submit(setup_request, url): (index, url) for (index, url) in enumerate(links)}
        for future in concurrent.futures.as_completed(future_to_url):

            (index, url) = future_to_url[future]
            
            try:
                responses[index] = future.result()  
            except Exception:
                info('Could not get a response from ' + url)
                responses[index] = available_on_wbm(url)

    return responses


def available_on_wbm(url):
    """ Checks if a given url has an archived snapshot on the wayback machine (internet archive). """

    # If option disabled in settings file, return None
    if not USE_WBM:
         return NO_RESPONSE

    # Send request to API and store content
    response_content =requests.get(WBM_API + url).content
    
    # Attempt to parse response content
    try:
        response_json = json.loads(response_content)
    except JSONDecodeError:
        info('Response from wayback machine api contained invalid JSON. (' + response_content + ')')

    # Extract fields from JSON response, by default all are set to empty dicts
    snapshots = response_json.get('archived_snapshots', {})
    closest_snapshot = snapshots.get('closest', {})
    snapshot_status = closest_snapshot.get('status', {})

    # If snapshots is an empty dict then no snapshot is available for the respective site 
    if snapshots == {}:
        return NO_RESPONSE
    # Othweise, if the status of the available snapshot is 200, return WBM to show its availability 
    else:
        return WAYBACK_MACHINE if snapshot_status == '200' else NO_RESPONSE


def setup_request(url):
    """ Sets up and returns web request. """

    # If the url is blank/empty, return empty string
    if url == '':
        return EMPTY

    # Otherwise return request
    else: 
        return requests.get(url, 
                            verify=VERIFY_CERT, 
                            timeout=REQUEST_TIMEOUT)


def format_links(links):
    """ Formats links. Removes whitespace, http:// and https:// and attempts to correct some errors. """

    # For every link in list of links
    for i in range(len(links)):

        # Convert to lower case and remove leading and trailing whitespace
        links[i] = links[i].lower().strip()

        ## Unsure about regular expressions? Try and copy the expression (eg, ^\s*$) into this site https://regex101.com/ for an explanation
        # If link consists of only whitespace, set to empty string
        links[i] = re.sub(r'^\s*$', '', links[i])

        # Remove https and http from start, account for possible :; and /\ typo
        links[i] = re.sub(r'https{0,1}(:|;)\/\/', '', links[i])

        # If a link doesnt now begin with www. add it to the start 
        if not links[i].startswith('www.') and links[i] != '':
            links[i] = 'www.' + links[i]

        # Append http:// to the start of each 
        if links[i] != '':
            links[i] = 'http://' + links[i]

    return links

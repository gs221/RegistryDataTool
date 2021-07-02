from requests.api import head
from helpers import get_delimiter, get_file_path
from os import sep
import pandas as pd
from pandas import DataFrame
import requests
import re
import validators
from threading import Thread
import csv

def check_links():
  # Get file path
  file_path = get_file_path('./data/org/', 'Please ensure the Org data is in the org folder. The folder can only contain a single file.')

  # Detect delimiter being used in data
  sep = get_delimiter(file_path, 'iso-8859-15')

  # Open csv file
  with open(file_path, 'r', encoding='iso-8859-15') as un_checked, open('links-checked.csv', 'w') as checked:
    csv_reader = csv.reader(un_checked, delimiter=sep)
    csv_writer = csv.writer(checked)

    # Read headings and add new column at beginning 
    headings = next(csv_reader)
    headings.insert(0, 'Link-Check')

    # Write headings to file 
    csv_writer.writerow(headings)


    exit(0)




def check_link(link: str) -> str:
  requests.packages.urllib3.disable_warnings()
  
  link = format_link(link)
  
  try: 
    if requests.get('https://' + link, timeout=5, verify=False).status_code == 200:
      #print('OK : ' + link)
      return 'OK'
    elif requests.get('http://' + link, timeout=5, verify=False).status_code == 200:
      #print('OK : ' + link)
      return 'OK'
    else:
      #print('ERR : ' + link)
      return 'ER'
  except:
    #print('ERR: ' + link)
    return 'EX'

def format_link(link: str) -> str:
  # Convert to lower case and remove leading and trailing whitespace
  link = link.lower().strip()

  # If link is empty then return 
  if link == '': return ''

  # remove https and http from start
  link = re.sub('https{0,1}(:|;)\/\/', '', link)

  return link
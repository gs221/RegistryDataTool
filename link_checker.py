from os import sep
import pandas as pd
from pandas import DataFrame
import requests

def check_links():
  data: DataFrame = pd.read_csv('./data/org/men_org.csv', sep=',', dtype=str, encoding='iso-8859-15', keep_default_na=False)

  for link in data['Web URL']:
    if link != '': print(str(requests.get(link, verify=False).status_code) + ' : ' + link)
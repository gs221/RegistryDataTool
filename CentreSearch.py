from os import remove, sep
import pandas as pd
from pandas import DataFrame
from fuzzywuzzy import fuzz

# Searches for centres that now use UCAS code 
def centre_search(ucas: DataFrame, internal: DataFrame):

    # Remove records from UCAS data where corresponding school with ID is already in internal data
    removed_common = ucas[ucas['School'].isin(internal['School code']) == False]

    # Get schools that now have UCAS code 
    duplicates = internal[internal['Postcode'].isin(removed_common['Postcode'])]
    
    print(duplicates)

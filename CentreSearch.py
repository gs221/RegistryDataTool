from os import remove, sep
import pandas as pd
from pandas import DataFrame
from fuzzywuzzy import fuzz

# Searches for centres that now use UCAS code 
def centre_search(ucas: DataFrame, internal: DataFrame):

    # Remove records from UCAS data where corresponding school with ID is already in internal data
    removed_common = ucas[ucas['School'].isin(internal['School code']) == False]
    
    # Remove UCAS codes and other malformed codes leaving only internal codes
    without_ucas = internal[internal['School code'].str.contains(r'^[a-zA-Z]{2}\d{3,5}$', na=False)]

    print(without_ucas)

    # Certain matches
    #for in_school in without_ucas['Full name']:
    #    certain_matches = without_ucas[without_ucas['Full name'].isin(removed_common['School Name'])]

    #print(certain_matches)

    # Find possible matches 
    #for in_school in without_ucas['Full name']:
    #    for ucas_school in removed_common['School Name']:
    #        if fuzz.ratio(in_school, ucas_school) > 70:
    #            print(in_school, " : ", ucas_school)
    
    #duplicates = ucas[ucas.duplicated(subset=['School Name', 'Address line 1', 'Address line 2', 'Address line 3', 'Address line 4', 'Postcode'])]
    
    #print(duplicates[['School', 'School Name']].to_csv())

    #existing_removed = remove_existing(ucas, internal)


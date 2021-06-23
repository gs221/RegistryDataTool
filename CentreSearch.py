
import os
import shutil

from pandas import DataFrame
from csvlink import csvlink
from FileManager import format_results

# Searches for centres that now use UCAS code 
def centre_search(ucas: DataFrame, internal: DataFrame):

    # Remove records from UCAS data where corresponding school with ID is already in internal data
    removed_common = ucas[ucas['School'].isin(internal['School code']) == False]

    # Remove UCAS codes and other malformed codes leaving only internal codes
    without_ucas = internal[internal['School code'].str.contains(r'^[a-zA-Z]{2}\d{3,5}$', na=False)]
    
    # Generate directory for pandas generated csv files
    if not os.path.exists('./in'):
        os.mkdir('./in')
    else:
        shutil.rmtree('./in')
        os.mkdir('./in')

    # Generate files and place in directory
    removed_common.to_csv('./in/ucas.csv', index=False)
    without_ucas.to_csv('./in/scl.csv', index=False)

    # Run CSV Link
    linker = csvlink.CSVLink()
    linker.run()

    # Remove in directory 
    if os.path.exists('./in'):
        shutil.rmtree('./in')

    # Format results
    format_results('potential_matches.csv', 'scl_only.csv', 'ucas_only.csv')
    

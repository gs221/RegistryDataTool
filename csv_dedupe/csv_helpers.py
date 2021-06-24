import os
import re
import csv
import logging
import sys
import platform
import dedupe

from io import StringIO, open

from dedupe.api import RecordLink
from helpers import try_again
    
if platform.system() != 'Windows' :
    from signal import signal, SIGPIPE, SIG_DFL
    signal(SIGPIPE, SIG_DFL)


def preProcess(column):
    """
    Do a little bit of data cleaning. Things like casing, extra spaces, 
    quotes and new lines are ignored.
    """
    column = re.sub('  +', ' ', column)
    column = re.sub('\n', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    
    if column == '' :
        column = None
    return column


def readData(input_file, field_names, delimiter=',', prefix=None) -> dict:
    """
    Read in our data from a CSV file and create a dictionary of records, 
    where the key is a unique record ID and each value is a dict 
    of the row fields.

    **Currently, dedupe depends upon records' unique ids being integers
    with no integers skipped. The smallest valued unique id must be 0 or
    1. Expect this requirement will likely be relaxed in the future.**
    """

    data = {}
    
    reader = csv.DictReader(StringIO(input_file),delimiter=delimiter)
    for i, row in enumerate(reader):
        clean_row = {k: preProcess(v) for (k, v) in row.items() if k is not None}
        if prefix:
            row_id = u"%s|%s" % (prefix, i)
        else:
            row_id = i
        data[row_id] = clean_row

    return data


def writeLinkedResults(clustered_pairs, input_1, input_2, potential_matches, ucas_only, scl_only , inner_join=False) -> None:
    """ Writes results when two csv files are being searched for duplicates. 
        - Potential matches: written to a file with combined headers. 
        - Records unique to scl: written to a file with specified name.
        - Records unique to ucas: written to a file with specified name. 
    """

    print('[INFO] Saving potential matches to: ', potential_matches.name)
    print('[INFO] Saving schools that only appeared in ucas data to: ', ucas_only.name)
    print('[INFO] Saving schools that only appeared in scl data to ', scl_only.name)

    matched_records = []
    seen_1 = set()
    seen_2 = set()

    input_1 = [row for row in csv.reader(StringIO(input_1))]
    row_header = input_1.pop(0)

    input_2 = [row for row in csv.reader(StringIO(input_2))]
    row_header_2 = input_2.pop(0)
    
    all_headers = row_header + row_header_2

    for pair in clustered_pairs:
        index_1, index_2 = [int(index.split('|', 1)[1]) for index in pair[0]]

        matched_records.append(input_1[index_1] + input_2[index_2])
        seen_1.add(index_1)
        seen_2.add(index_2)

    # Create csv writers for all output files using passed in filenames
    match_writer = csv.writer(potential_matches)
    ucas_writer = csv.writer(ucas_only)
    scl_writer = csv.writer(scl_only)

    # Write headings to each of the output files 
    match_writer.writerow(all_headers)
    scl_writer.writerow(row_header)
    ucas_writer.writerow(row_header_2)

    # Write all matches to file 
    for matches in matched_records:
        match_writer.writerow(matches)

    if not inner_join:

        # Print rows that were only in input one 
        for i, row in enumerate(input_1):
            if i not in seen_1:
                scl_writer.writerow(row)

        # Print rows that were only in input two
        for i, row in enumerate(input_2):
            if i not in seen_2:
                ucas_writer.writerow(row)


class CsvSetup(object) :
    def __init__(self, configuration: dict) -> None :
        """ Initialises configuration information for the CSVCommand class. """ 

        # Initialise configuration 
        self.configuration = configuration

        # Set values from config file, or use defaults
        self.potential_matches = self.configuration.get('matches_file', None)
        self.ucas_only = self.configuration.get('ucas_only_file', None)
        self.scl_only = self.configuration.get('scl_only_file', None)
        self.training_file = self.configuration.get('training_file', './data/training/training.json')
        self.settings_file = self.configuration.get('settings_file', './data/training/cached_settings')
        self.sample_size = self.configuration.get('sample_size', 1500)
        self.recall_weight = self.configuration.get('recall_weight', 1)
        self.delimiter = self.configuration.get('delimiter',',')

        # Determine whether or not program should skip training
        self.skip_training = ask_to_train()

        # Must use this method as 'field definition' is itself a dictionary 
        if 'field_definition' in self.configuration:
            self.field_definition = self.configuration['field_definition']
        else :
            self.field_definition = None

        # Check if necessary training files exist should user opt to skip training 
        while self.skip_training and not (os.path.exists(self.training_file) and os.path.exists(self.settings_file)):
            print('\n[ERROR] Could not find training data. Please ensure that the following files are present:\n\t- ', self.training_file, '\n\t- ', self.settings_file, '\n')
            try_again()

        # Check if training folder is empty should user opt to train 
        while not self.skip_training and (os.path.exists(self.training_file) or os.path.exists(self.settings_file)):
            print('[ERROR] Please remove existing training data from training folder.')
            try_again()


    def dedupe_training(self, deduper: RecordLink) -> None:
        """ Loads existing training data, or starts manual training process. """

        if os.path.exists(self.training_file):
            logging.info('Reading labeled examples from %s' %
                         self.training_file)
            with open(self.training_file) as tf:
                deduper.readTraining(tf)

        if not self.skip_training:
            logging.info('Starting active labeling...')

            dedupe.consoleLabel(deduper)

            # When finished, save our training away to disk
            logging.info('Saving training data to %s' % self.training_file)
            if sys.version < '3' :
                with open(self.training_file, 'wb') as tf:
                    deduper.writeTraining(tf)
            else :
                with open(self.training_file, 'w') as tf:
                    deduper.writeTraining(tf)
        else:
            logging.info('Skipping the training step')

        deduper.train()

        # After training settings have been established make a cache file for reuse
        logging.info('Caching training result set to file %s' % self.settings_file)
        with open(self.settings_file, 'wb') as sf:
            deduper.writeSettings(sf)


def ask_to_train() -> bool:
  """ Asks the user if they wish to train the program or use existing training data. Returns true/false. """

  while True:
    value = input("Would you like to run with existing training data? (y/n) ").lower()
    if value == 'y' or value == 'yes': return True
    if value == 'n' or value == 'no': return False
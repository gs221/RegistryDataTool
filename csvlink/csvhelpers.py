from future.builtins import next

import os
import re
import glob
import logging
from io import StringIO, open
import sys
import platform
if sys.version < '3' :
    from backports import csv
else :
    import csv

if platform.system() != 'Windows' :
    from signal import signal, SIGPIPE, SIG_DFL
    signal(SIGPIPE, SIG_DFL)

import dedupe
import json

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


def readData(input_file, field_names, delimiter=',', prefix=None):
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


# ## Writing results
def writeLinkedResults(clustered_pairs, input_1, input_2, potential_matches, ucas_only, scl_only , inner_join=False):
    logging.info('[INFO] Saving potential matches to: %s' % potential_matches)

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

    match_writer = csv.writer(potential_matches)
    ucas_writer = csv.writer(ucas_only)
    scl_writer = csv.writer(scl_only)

    match_writer.writerow(all_headers)
    scl_writer.writerow(row_header)
    ucas_writer.writerow(row_header_2)

    for matches in matched_records:
        match_writer.writerow(matches)

    if not inner_join:

        for i, row in enumerate(input_1):
            if i not in seen_1:
                scl_writer.writerow(row)

        for i, row in enumerate(input_2):
            if i not in seen_2:
                ucas_writer.writerow(row)

class CSVCommand(object) :
    def __init__(self) :

        self.configuration = {}

        #read from configuration file
        try:
            with open('./csvlink/config.json', 'r') as f:
                config = json.load(f)
                self.configuration.update(config)
        except IOError:
            raise self.parser.error(
                "Could not find config file. Did you name it correctly?")

        # Set values from config file, or use defaults
        self.potential_matches = self.configuration.get('matches_file', None)
        self.ucas_only = self.configuration.get('ucas_only_file', None)
        self.scl_only = self.configuration.get('scl_only_file', None)
        
        selection = input("Would you like to run with existing training data? (y/n) ")

        if selection == 'y':
            self.skip_training = True
        elif selection == 'n':

            if len(glob.glob(os.path.join('./data/training/', '*.*'))) > 0:
                print('\n[ERROR] Training folder not empty. Please remove any training data from this folder, or select y(es) in previous option to run with exsting data.\n')
                exit(0)
            else:
                self.skip_training = False

        else:
            print('[ERROR] Invalid selection. Re-run and enter either \'y\' or \'n\'')        

        self.training_file = './data/training/training.json'
        self.settings_file = './data/training/cached_settings'
        self.sample_size = self.configuration.get('sample_size', 1500)
        self.recall_weight = self.configuration.get('recall_weight', 1)

        self.delimiter = self.configuration.get('delimiter',',')

        # backports for python version below 3 uses unicode delimiters
        if sys.version < '3':
            self.delimiter = unicode(self.delimiter)

        if 'field_definition' in self.configuration:
            self.field_definition = self.configuration['field_definition']
        else :
            self.field_definition = None

        if self.skip_training and not (os.path.exists(self.training_file) or os.path.exists(self.settings_file)):
            print('\n[ERROR] Could not find training data. Please ensure that the following files are present:\n\t- ', self.training_file, '\n\t- ', self.settings_file, '\n')
            exit(0)


    # If we have training data saved from a previous run of dedupe,
    # look for it an load it in.
    def dedupe_training(self, deduper) :

        # __Note:__ if you want to train from scratch, delete the training_file
        if os.path.exists(self.training_file):
            logging.info('reading labeled examples from %s' %
                         self.training_file)
            with open(self.training_file) as tf:
                deduper.readTraining(tf)

        if not self.skip_training:
            logging.info('starting active labeling...')

            dedupe.consoleLabel(deduper)

            # When finished, save our training away to disk
            logging.info('saving training data to %s' % self.training_file)
            if sys.version < '3' :
                with open(self.training_file, 'wb') as tf:
                    deduper.writeTraining(tf)
            else :
                with open(self.training_file, 'w') as tf:
                    deduper.writeTraining(tf)
        else:
            logging.info('skipping the training step')

        deduper.train()

        # After training settings have been established make a cache file for reuse
        logging.info('caching training result set to file %s' % self.settings_file)
        with open(self.settings_file, 'wb') as sf:
            deduper.writeSettings(sf)

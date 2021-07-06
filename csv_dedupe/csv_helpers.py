import os
import re
import csv
import sys
import dedupe
import logging
import platform

from helpers import info
from io import StringIO, open
from settings import A_ONLY, B_ONLY, DATA_PATH, POTENTIAL_DUPLICATES, POTENTIAL_MATCHES, TRAINING_PATH

if platform.system() != 'Windows':
    from signal import signal, SIGPIPE, SIG_DFL

    signal(SIGPIPE, SIG_DFL)


def pre_process(column):
    """
    Do a little bit of data cleaning. Things like casing, extra spaces, 
    quotes and new lines are ignored.
    """
    column = re.sub('  +', ' ', column)
    column = re.sub('\n', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()

    if column == '':
        column = None
    return column


def readData(input_file, delimiter=',', prefix=None) -> dict:
    """
    Read in our data from a CSV file and create a dictionary of records, 
    where the key is a unique record ID and each value is a dict 
    of the row fields.

    **Currently, dedupe depends upon records' unique ids being integers
    with no integers skipped. The smallest valued unique id must be 0 or
    1. Expect this requirement will likely be relaxed in the future.**
    """

    data = {}

    reader = csv.DictReader(StringIO(input_file), delimiter=delimiter)
    for i, row in enumerate(reader):
        clean_row = {k: pre_process(v) for (k, v) in row.items() if k is not None}
        if prefix:
            row_id = u"%s|%s" % (prefix, i)
        else:
            row_id = i
        data[row_id] = clean_row

    return data


def write_results(clustered_dupes, input_file, results_file):
    """ Writes original data back out to a CSV with a new column called 'Cluster ID' indicating which records refer to each other. """

    info('Saving results to ' + results_file.name)

    cluster_membership = {}
    for cluster_id, (cluster, score) in enumerate(clustered_dupes):
        for record_id in cluster:
            cluster_membership[record_id] = cluster_id

    unique_record_id = cluster_id + 1

    writer = csv.writer(results_file)

    reader = csv.reader(StringIO(input_file))

    heading_row = next(reader)
    heading_row.insert(0, u'Cluster ID')
    writer.writerow(heading_row)

    for row_id, row in enumerate(reader):
        if row_id in cluster_membership:
            cluster_id = cluster_membership[row_id]
        else:
            cluster_id = unique_record_id
            unique_record_id += 1
        row.insert(0, cluster_id)
        writer.writerow(row)


def write_linked_results(clustered_pairs, input_1, input_2, potential_matches, a_only, b_only,
                         inner_join=False) -> None:
    """ Writes results when two csv files are being searched for duplicates. 
        - Potential matches: written to a file with combined headers. 
        - Records unique to first file written to file a_only.csv.
        - Records unique to second file written to file b_only.csv.\n 
        NB: Only used in csv_linker.
    """

    info('Saving potential matches to: ' + potential_matches.name)
    info('Saving records that only appeared in data_a data to: ' + a_only.name)
    info('Saving records that only appeared in data_b data to: ' + b_only.name)

    matched_records = []
    seen_1 = set()
    seen_2 = set()

    input_1 = [row for row in csv.reader(StringIO(input_1))]
    row_header = input_1.pop(0)

    input_2 = [row for row in csv.reader(StringIO(input_2))]
    row_header_2 = input_2.pop(0)

    all_headers = ['Match'] + row_header + row_header_2

    for pair in clustered_pairs:
        index_1, index_2 = [int(index.split('|', 1)[1]) for index in pair[0]]

        matched_records.append(input_1[index_1] + input_2[index_2])
        seen_1.add(index_1)
        seen_2.add(index_2)

    # Create csv writers for all output files using passed in filenames
    match_writer = csv.writer(potential_matches)
    a_only_writer = csv.writer(a_only)
    b_only_writer = csv.writer(b_only)

    # Write headings to each of the output files 
    match_writer.writerow(all_headers)
    a_only_writer.writerow(row_header)
    b_only_writer.writerow(row_header_2)

    # Write all matches to file 
    for matches in matched_records:
        match_writer.writerow([''] + matches)

    if not inner_join:

        # Print rows that were only in input one 
        for i, row in enumerate(input_1):
            if i not in seen_1:
                a_only_writer.writerow(row)

        # Print rows that were only in input two
        for i, row in enumerate(input_2):
            if i not in seen_2:
                b_only_writer.writerow(row)


class CsvSetup(object):
    def __init__(self, conf_a) -> None:
        """ Initialises configuration information for the CsvSetup class. """

        # File names for record matcher 
        self.potential_matches = POTENTIAL_MATCHES
        self.a_only = A_ONLY
        self.b_only = B_ONLY

        # File name for duplicate detector
        self.results_file = POTENTIAL_DUPLICATES

        # Training files
        self.training_file = DATA_PATH + TRAINING_PATH + 'training.json'
        self.settings_file = DATA_PATH + TRAINING_PATH + 'cached_settings'

        # Set recall weight from config 
        self.recall_weight = conf_a.recall_weight

        # Dedupe Settings. These are only configurable here.
        self.sample_size = 1500
        self.delimiter = ','
        self.skip_training = False  # Always false to make program simpler, users must always train AI

        # Delete existing training data should any be present
        if os.path.exists(self.training_file):
            os.remove(self.training_file)
        if os.path.exists(self.settings_file):
            os.remove(self.settings_file)

    def dedupe_training(self, deduper) -> None:
        """ Loads existing training data, or starts manual training process. """

        if os.path.exists(self.training_file):
            logging.info('Reading labeled examples from %s' % self.training_file)
            with open(self.training_file) as tf:
                deduper.readTraining(tf)

        if not self.skip_training:
            logging.info('Starting active labeling...')

            dedupe.consoleLabel(deduper)

            # When finished, save our training away to disk
            logging.info('Saving training data to %s' % self.training_file)
            
            # Create directory for training information 
            if not os.path.exists(DATA_PATH + TRAINING_PATH):
                os.mkdir(DATA_PATH + TRAINING_PATH)
            
            # Write training data to training folder
            with open(self.training_file, 'w') as tf:
                deduper.writeTraining(tf)
        else:
            logging.info('Skipping the training step')

        deduper.train()

        # After training settings have been established make a cache file for reuse
        logging.info('Caching training result set to file %s' % self.settings_file)
        with open(self.settings_file, 'wb') as sf:
            deduper.writeSettings(sf)

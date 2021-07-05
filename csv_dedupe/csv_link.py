import os
import dedupe
import logging

from io import open
from . import csv_helpers
from helpers import error


class CsvLink(csv_helpers.CsvSetup):
    def __init__(self, conf_a, conf_b):
        super(CsvLink, self).__init__(conf_a)

        """ Following initialisation, sets up input files and fields for linker. """

        from record_matcher import TEMP_PATH
        from configuration_manager import DATA_PATH

        input_one = DATA_PATH + TEMP_PATH + 'temp_a.csv'
        input_two = DATA_PATH + TEMP_PATH + 'temp_b.csv'

        try:
            self.input_1 = open(input_one, encoding='utf-8').read()
        except IOError:
            error('Could not find input file at ' + input_one)

        try:
            self.input_2 = open(input_two, encoding='utf-8').read()
        except IOError:
            error('Could not find input file at ' + input_two)


        # Set field names from configuration files
        self.field_names_1 = conf_a.column_names
        self.field_names_2 = conf_b.column_names
        
        # Dedupe settings. Not modifiable via config
        self.inner_join = False
        self.field_definition = [{'field': field, 'type': 'String'} for field in self.field_names_1]


    def run(self) -> None:
        """ Runs the linking program. """

        # Read configured csv files
        data_1 = csv_helpers.readData(self.input_1, delimiter=self.delimiter, prefix='input_1')
        data_2 = csv_helpers.readData(self.input_2, delimiter=self.delimiter, prefix='input_2')

        # sanity check for provided field names in CSV file
        for field in self.field_names_1:
            if field not in list(data_1.values())[0]:
                error("Could not find field '" + field + "' in input")

        for field in self.field_names_2:
            if field not in list(data_2.values())[0]:
                error("Could not find field '" + field + "' in input")

        if self.field_names_1 != self.field_names_2:
            for record_id, record in data_2.items():
                remapped_record = {}
                for new_field, old_field in zip(self.field_names_1, self.field_names_2):
                    remapped_record[new_field] = record[old_field]
                    data_2[record_id] = remapped_record

        logging.info('imported %d rows from file 1', len(data_1))
        logging.info('imported %d rows from file 2', len(data_2))

        logging.info('using fields: %s' % [field['field'] for field in self.field_definition])

        if self.skip_training and os.path.exists(self.settings_file):

            # Load our deduper from the last training session cache.
            logging.info('reading from previous training cache %s' % self.settings_file)
            with open(self.settings_file, 'rb') as f:
                deduper = dedupe.StaticRecordLink(f)

            fields = {variable.field for variable in deduper.data_model.primary_fields}
            (nonexact_1, nonexact_2, exact_pairs) = exact_matches(data_1, data_2, fields)

        else:
            # Create a new deduper object and pass our data model to it.
            deduper = dedupe.RecordLink(self.field_definition)

            fields = {variable.field for variable in deduper.data_model.primary_fields}
            (nonexact_1, nonexact_2, exact_pairs) = exact_matches(data_1, data_2, fields)

            # Set up our data sample
            logging.info('taking a sample of %d possible pairs', self.sample_size)
            deduper.sample(nonexact_1, nonexact_2, self.sample_size)

            # Perform standard training procedures
            self.dedupe_training(deduper)

        # ## Blocking
        logging.info('blocking...')

        # ## Clustering

        # Find the threshold that will maximize a weighted average of our precision and recall. 
        # When we set the recall weight to 2, we are saying we care twice as much
        # about recall as we do precision.
        #
        # If we had more data, we would not pass in all the blocked data into
        # this function but a representative sample.

        logging.info('finding a good threshold with a recall_weight of %s' % self.recall_weight)
        threshold = deduper.threshold(data_1, data_2, recall_weight=self.recall_weight)

        # `duplicateClusters` will return sets of record IDs that dedupe
        # believes are all referring to the same entity.

        logging.info('clustering...')
        clustered_dupes = deduper.match(data_1, data_2, threshold)

        clustered_dupes.extend(exact_pairs)

        logging.info('# duplicate sets %s' % len(clustered_dupes))

        write_function = csv_helpers.write_linked_results

        # write out our results
        with open(self.potential_matches, 'w', encoding='utf-8') as pm, \
                open(self.a_only, 'w', encoding='utf-8') as scl, \
                open(self.b_only, 'w', encoding='utf-8') as ucas:
            write_function(clustered_dupes, self.input_1, self.input_2, pm, ucas, scl, self.inner_join)


def exact_matches(data_1, data_2, match_fields):
    """ Identifies exact and non-exact matches between data sets. """

    nonexact_1 = {}
    nonexact_2 = {}
    exact_pairs = []
    redundant = {}

    for key, record in data_1.items():
        record_hash = hash(tuple(record[f] for f in match_fields))
        redundant[record_hash] = key

    for key_2, record in data_2.items():
        record_hash = hash(tuple(record[f] for f in match_fields))
        if record_hash in redundant:
            key_1 = redundant[record_hash]
            exact_pairs.append(((key_1, key_2), 1.0))
            del redundant[record_hash]
        else:
            nonexact_2[key_2] = record

    for key_1 in redundant.values():
        nonexact_1[key_1] = data_1[key_1]

    return nonexact_1, nonexact_2, exact_pairs

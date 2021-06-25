import os
import sys
import logging
import dedupe

from io import open
from . import csv_helpers
from helpers import print_err


class CsvDedupe(csv_helpers.CsvSetup) :
    def __init__(self, configuration: dict):
        super(CsvDedupe, self).__init__(configuration)
        
        """ Following initialisation, sets up input file and fields for deduper. """

        try:
            self.input = open(self.configuration['input'], encoding='utf-8').read()
        except IOError:
            print_err('[ERROR] Could not find input file at ' + self.configuration['input'])


        if self.field_definition is None :
            try:
                self.field_names = self.configuration['field_names']
                self.field_definition = [{'field': field,
                                          'type': 'String'}
                                         for field in self.field_names]
            except KeyError:
                print_err('[ERROR] You must provide field names in configuration file.')
        else :
            self.field_names = [field_def['field'] for field_def in self.field_definition]

        self.destructive = self.configuration.get('destructive', False)


    def run(self):
        """ Runs the deduper program. """

        data_d = {}

        # import the specified CSV file
        data_d = csv_helpers.readData(self.input, self.field_names, delimiter=self.delimiter)

        logging.info('imported %d rows', len(data_d))

        # sanity check for provided field names in CSV file
        for field in self.field_definition:
            if field['type'] != 'Interaction':
                if not field['field'] in data_d[0]:
                    print_err("Could not find field '" + field + "' in input")

        logging.info('using fields: %s' % [field['field'] for field in self.field_definition])

        if self.skip_training and os.path.exists(self.settings_file):

            # Load our deduper from the last training session cache.
            logging.info('reading from previous training cache %s' % self.settings_file)
            with open(self.settings_file, 'rb') as f:
                deduper = dedupe.StaticDedupe(f)

            fields = {variable.field for variable in deduper.data_model.primary_fields}
            unique_d, parents = exact_matches(data_d, fields)
                
        else:
            # # Create a new deduper object and pass our data model to it.
            deduper = dedupe.Dedupe(self.field_definition)

            fields = {variable.field for variable in deduper.data_model.primary_fields}
            unique_d, parents = exact_matches(data_d, fields)

            # Set up our data sample
            logging.info('taking a sample of %d possible pairs', self.sample_size)
            deduper.sample(unique_d, self.sample_size)

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
        threshold = deduper.threshold(unique_d, recall_weight=self.recall_weight)

        # `duplicateClusters` will return sets of record IDs that dedupe
        # believes are all referring to the same entity.

        logging.info('clustering...')
        clustered_dupes = deduper.match(unique_d, threshold)

        expanded_clustered_dupes = []
        for cluster, scores in clustered_dupes:
            new_cluster = list(cluster)
            new_scores = list(scores)
            for row_id, score in zip(cluster, scores):
                children = parents.get(row_id, [])
                new_cluster.extend(children)
                new_scores.extend([score] * len(children))
            expanded_clustered_dupes.append((new_cluster, new_scores))

        clustered_dupes = expanded_clustered_dupes

        logging.info('# duplicate sets %s' % len(clustered_dupes))

        write_function = csv_helpers.writeResults
        # write out our results
        if self.destructive:
            write_function = csv_helpers.writeUniqueResults

        if self.results_file:
            with open(self.results_file, 'w', encoding='utf-8') as results_file:
                write_function(clustered_dupes, self.input, results_file)
        else:
            write_function(clustered_dupes, self.input, sys.stdout)

def exact_matches(data_d, match_fields):
    unique = {}
    redundant = {}
    for key, record in data_d.items():
        record_hash = hash(tuple(record[f] for f in match_fields))
        if record_hash not in redundant:
            unique[key] = record
            redundant[record_hash] = (key, [])
        else:
            redundant[record_hash][1].append(key)

    return unique, {k : v for k, v in redundant.values()}


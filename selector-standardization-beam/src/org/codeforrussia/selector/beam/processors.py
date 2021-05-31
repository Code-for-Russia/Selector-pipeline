import time

import apache_beam as beam
from apache_beam.runners.common import GlobalWindow
from apache_beam.utils.windowed_value import WindowedValue

from org.codeforrussia.selector.standardizer.common import Standardizer


class StandardizationBeamProcessor(beam.DoFn):
    """
    Beam processor that applies a given standardizer to batched data
    """
    BATCH_SIZE = 1  # in case of when batch inference is efficient

    def __init__(self, standardizer: Standardizer):
        self.batch = list()
        self.standardizer = standardizer

    def setup(self):
        pass

    def process(self, element, *args, **kwargs):
        self.batch.append(element)
        if len(self.batch) >= self.BATCH_SIZE:
            return self.finish_batch()

    def finish_bundle(self):
        return self.finish_batch()

    def finish_batch(self):
        if self.batch:
            processed_batch = self.standardizer.convert_batch(self.batch)
            self.clear_batch()
            for e in processed_batch:
                if e is not None: # filter out empty results
                    yield WindowedValue(e, time.time(), [GlobalWindow()])

    def clear_batch(self):
        self.batch = list()



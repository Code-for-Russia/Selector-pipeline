import os.path, sys

f = __file__
for _ in range(6): # dirty hack to make custom Beam modules work in Airflow
    f = os.path.dirname(f)
sys.path.insert(0, f)

print(sys.path)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/opt/airflow/google-configs/carbide-program-314404-b1f3be733966.json"

import argparse
from typing import Dict

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToAvro
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions

from org.codeforrussia.selector.pipeline.beam.processors import StandardizationBeamProcessor
from pathlib import Path
import json
import logging
from org.codeforrussia.selector.pipeline.input.dump_formats import SupportedInputFormat
from org.codeforrussia.selector.standardizers.common import Standardizer
from org.codeforrussia.selector.standardizers.schema_registry import StandardProtocolSchemaRegistry
from org.codeforrussia.selector.standardizers.custom.shpilkin import ShpilkinDumpStandardizer

def run(argv=None, save_main_session=True):
    parser = argparse.ArgumentParser()

    parser.add_argument('--input',
                        dest='input',
                        required=True,
                        help='Input file to process')

    parser.add_argument('--output',
                        dest='output',
                        required=True,
                        help='Output file to write results to')

    known_args, pipeline_args = parser.parse_known_args(argv)

    schema_registry = StandardProtocolSchemaRegistry()

    registered_schema_keys = schema_registry.get_all_registered_schema_keys()

    standardizers: Dict[SupportedInputFormat, Standardizer] = {
        SupportedInputFormat.SHPILKIN_DUMP : ShpilkinDumpStandardizer(schema_registry=schema_registry)
    }

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

    with beam.Pipeline(options=pipeline_options) as p:
        lines = p | 'ReadFromGCS' >> ReadFromText(known_args.input)
        processor = StandardizationBeamProcessor(standardizer=standardizers[SupportedInputFormat.SHPILKIN_DUMP])
        jsonsGroupedBySchema = (lines
                                | 'JSONLoads' >> beam.Map(json.loads)
                                | 'Process' >> beam.ParDo(processor)
                                | 'Partition' >> beam.Partition(lambda result, num_partitions: registered_schema_keys.index((result["election_attrs"]["level"], result["election_attrs"]["type"], result["election_attrs"]["location"])), len(registered_schema_keys)))

        for schema_key, jsons in zip(registered_schema_keys, jsonsGroupedBySchema):
            schema = schema_registry.search_schema(*schema_key)
            output_path = (Path(known_args.output) / schema["name"].replace(".", "_")).as_posix() + ".avro"
            (jsons
             | 'Map' >> beam.Map(lambda data: data["sdata"])
             | 'WriteToGCS' >> WriteToAvro(output_path, schema=schema))

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
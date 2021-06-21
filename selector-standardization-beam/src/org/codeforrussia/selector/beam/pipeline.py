import argparse

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToAvro
from apache_beam.options.pipeline_options import PipelineOptions

from pathlib import Path
import json
import logging

from org.codeforrussia.selector.standardizer.recognizers.protocol_field_recognizer_registry_factory import \
    ProtocolFieldRecognizerRegistryFactory
from org.codeforrussia.selector.standardizer.standardizer_registry_factory import SupportedInputFormat, \
    StandardizerRegistryFactory
from org.codeforrussia.selector.config.global_config import GlobalConfig
from org.codeforrussia.selector.standardizer.schemas.schema_registry_factory import StandardProtocolSchemaRegistryFactory

def add_gcp_connection(known_args):
    if known_args.google_application_credentials is not None:
        import os
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = known_args.google_application_credentials


def run(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--input',
                        dest='input',
                        required=True,
                        help='Input file to process')

    parser.add_argument('--input-data-format',
                        dest='input_data_format',
                        required=True,
                        type=SupportedInputFormat,
                        choices=SupportedInputFormat,
                        help=f'Input data format. Supported only: {list(SupportedInputFormat)}')

    parser.add_argument('--output',
                        dest='output',
                        required=True,
                        help='Output file to write results to')

    parser.add_argument('--google-application-credentials',
                        type=str,
                        dest='google_application_credentials',
                        required=True,
                        help='GCP connection key file path')

    parser.add_argument('--gcs-bucket-name',
                        dest='gcs_bucket_name',
                        type=str,
                        required=True,
                        help='Google Cloud Storage (GCS) root bucket name, where all prepared artifacts are stored, e.g. "codeforrussia-selector"')

    parser.add_argument('--ml-models-gcs-prefix',
                        dest='ml_models_gcs_prefix',
                        type=str,
                        required=True,
                        help='GCS dir name, where pre-trained machine learning models are stored, e.g. "ml-models"')

    known_args, pipeline_args = parser.parse_known_args(argv)

    add_gcp_connection(known_args)

    global_config=GlobalConfig(
        gcs_bucket=known_args.gcs_bucket_name,
        ml_models_gcs_prefix=known_args.ml_models_gcs_prefix,
        gcs_credentials=known_args.google_application_credentials,
    )

    schema_registry = StandardProtocolSchemaRegistryFactory.get_schema_registry()

    registered_schema_keys = schema_registry.get_all_registered_schema_keys()

    standardizer = StandardizerRegistryFactory.get_standardizer_registry(
        schema_registry_factory=StandardProtocolSchemaRegistryFactory,
        protocol_recognizer_registry_factory=ProtocolFieldRecognizerRegistryFactory,
        global_config=global_config,
    ).get_standardizer(known_args.input_data_format)

    pipeline_options = PipelineOptions(pipeline_args)

    with beam.Pipeline(options=pipeline_options) as p:
        lines = p | 'ReadFromText' >> ReadFromText(known_args.input)

        jsonsGroupedBySchema = (lines
                                | 'JSONLoads' >> beam.Map(json.loads)
                                | 'Process' >> beam.ParDo(lambda row: standardizer.convert_batch([row]))
                                | 'Partition' >> beam.Partition(lambda result, num_partitions: registered_schema_keys.index((result["election_attrs"]["level"], result["election_attrs"]["type"], result["election_attrs"]["location"])), len(registered_schema_keys)))

        for i, (schema_key, jsons) in enumerate(zip(registered_schema_keys, jsonsGroupedBySchema)):
            schema = schema_registry.search_schema(*schema_key)
            output_path = (Path(known_args.output) / schema["name"].replace(".", "_")).as_posix()
            (jsons
             | f'Map_{i}' >> beam.Map(lambda data: data["sdata"])
             | f'WriteToAvro_{i}' >> WriteToAvro(output_path, schema=schema, file_name_suffix=".avro"))

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
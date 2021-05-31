from airflow.utils.dates import days_ago
from airflow import models
from airflow.providers.apache.beam.operators.beam import (
    BeamRunPythonPipelineOperator,
)
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator

default_args = {
    'owner': 'airflow',
    'input_data_path': "gs://codeforrussia-selector/shpilkin_dumps/state_duma_shpilkin_dump.21-09-2020.jsonl",
    'output_local_data_path': '/opt/airflow/standardized-election-data',
    'output_cloud_data_path': "/standardized-election-data"
}



with models.DAG(
        "selector_standardize_electoral_data",
        default_args=default_args,
        start_date=days_ago(1),
        schedule_interval=None,
        tags=['selector'],
) as dag_native_python:

    start_standardize_pipeline_local_direct_runner = BeamRunPythonPipelineOperator(
        task_id="start_standardize_pipeline_direct_runner",
        py_file='/opt/airflow/dags/selector-standardization-flow/src/org/codeforrussia/selector/pipeline/beam/pipeline.py',
        pipeline_options={
                          "input": default_args["input_data_path"],
                          "output": default_args["output_local_data_path"],
                          },
        py_requirements=['apache-beam[gcp]==2.26.0'],
        py_interpreter='python3',
        py_system_site_packages=False,
    )

    upload_file = LocalFilesystemToGCSOperator(
        task_id="upload_to_gcs",
        src=default_args["output_local_data_path"],
        dst=default_args["output_cloud_data_path"],
        bucket="codeforrussia-selector",
    )

    start_standardize_pipeline_local_direct_runner >> upload_file
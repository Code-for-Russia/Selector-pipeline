from airflow.utils.dates import days_ago
from airflow import models
from airflow.providers.apache.beam.operators.beam import (
    BeamRunPythonPipelineOperator,
)

default_args = {
    'owner': 'airflow',
    'input_data_path': "gs://codeforrussia-selector/shpilkin_dumps/state_duma_shpilkin_dump.21-09-2020.jsonl",
    'input_data_format': 1,
    'output_data_path': 'gs://codeforrussia-selector/standardized-election-data'
}


with models.DAG(
        "selector_standardize_electoral_data",
        default_args=default_args,
        start_date=days_ago(1),
        schedule_interval=None,
        tags=['selector'],
) as dag_native_python:

    start_standardize_pipeline_local_direct_runner = BeamRunPythonPipelineOperator(
        task_id="start_standardize_pipeline_local_direct_runner",
        py_file='/opt/airflow/dags/selector-standardization-flow/src/org/codeforrussia/selector/pipeline/beam/pipeline.py',
        # py_file='gs://selector-pipeline/selector-standardization-flow/src/org/codeforrussia/selector/pipeline/beam/pipeline.py',
        # py_options=['-m'],
        pipeline_options={"input": default_args["input_data_path"], "output": default_args},
        py_requirements=['apache-beam[gcp]==2.26.0'],
        py_interpreter='python3',
        py_system_site_packages=False,
    )
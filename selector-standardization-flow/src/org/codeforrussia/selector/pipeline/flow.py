from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow import models
from airflow.providers.apache.beam.operators.beam import (
    BeamRunPythonPipelineOperator,
)
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from textwrap import dedent

AIRFLOW_HOME_DIR = "/opt/airflow"
# Working dirs
STANDARDIZED_DATA_FOLDER = "standardized-election-data"
OUTPUT_LOCAL_DATA_PATH = f"{AIRFLOW_HOME_DIR}/{STANDARDIZED_DATA_FOLDER}"

# Google cloud storage parameters
GCS_BUCKET = "codeforrussia-selector"
GCS_ML_MODELS_PREFIX = "ml-models"
GCS_INPUT_DATA_PATH = f"gs://{GCS_BUCKET}/shpilkin_dumps/*"
GCS_INPUT_DUMP_FORMAT = "SHPILKIN"
GCS_CREDENTIALS_FILE = f"{AIRFLOW_HOME_DIR}/google-configs/gcs-credentials.json"

default_args = {
    'owner': 'airflow',
    'schedule_interval': '@daily',
}

assert OUTPUT_LOCAL_DATA_PATH != ""

with models.DAG(
        "selector_standardize_electoral_data",
        default_args=default_args,
        start_date=days_ago(1),
        tags=['selector'],
) as dag_native_python:

    standardizing_pipeline = BeamRunPythonPipelineOperator(
        task_id="standardizing_pipeline",
        py_file='org.codeforrussia.selector.beam.pipeline',
        py_options=['-m'],
        pipeline_options={
                          "input": GCS_INPUT_DATA_PATH,
                          "input-data-format": GCS_INPUT_DUMP_FORMAT,
                          "output": OUTPUT_LOCAL_DATA_PATH,
                          "google-application-credentials": GCS_CREDENTIALS_FILE,
                          "gcs-bucket-name": GCS_BUCKET,
                          "ml-models-gcs-prefix": GCS_ML_MODELS_PREFIX,
                          },
        py_requirements=[
            "apache-beam[gcp]==2.29.0",
            "selector-standardizers>=0.8.3",
            "selector-standardization-beam>=0.4.15",
        ],
        py_interpreter='python3',
        py_system_site_packages=False,
    )

    upload_to_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_standardized_data_to_gcs",
        src=f"{OUTPUT_LOCAL_DATA_PATH}/*.avro",
        bucket="codeforrussia-selector",
        dst=f"{STANDARDIZED_DATA_FOLDER}/" + dedent("{{ds}}/"), # output data grouped in the today-date folder
    )

    cleanup_local_data = BashOperator(
       task_id="cleanup_local_data",
       bash_command=f"rm -rf {OUTPUT_LOCAL_DATA_PATH}/*",
    )

    standardizing_pipeline >> upload_to_gcs >> cleanup_local_data
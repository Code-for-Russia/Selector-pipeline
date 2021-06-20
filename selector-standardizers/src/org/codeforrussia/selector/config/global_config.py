from dataclasses import dataclass


@dataclass
class GlobalConfig:
    # Google Cloud Storage (GCS) root bucket name, where all prepared artifacts are stored, e.g. "codeforrussia-selector"
    gcs_bucket: str
    # GCS dir name, where pre-trained machine learning models are stored, e.g. "ml-models"
    ml_models_gcs_prefix: str
    # Path to GCS credentials file, being read from GOOGLE_APPLICATION_CREDENTIALS environment variable
    gcs_credentials: str = None

    def __post_init__(self):
        if self.gcs_credentials is None:
            import os
            self.gcs_credentials = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            assert self.gcs_credentials is not None, "GOOGLE_APPLICATION_CREDENTIALS environment variable must be set"
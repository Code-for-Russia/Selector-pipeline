from google.cloud import storage

class GCS:
    def __init__(self):
        self.client = storage.Client()

    def download_file(self, bucket_name: str, filename: str, output_local_filename: str):
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.download_to_filename(output_local_filename)
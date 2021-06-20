import zipfile

def unzip(filepath: str, output_dir: str):
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
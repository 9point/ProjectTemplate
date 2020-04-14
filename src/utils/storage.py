import boto3
import os

_AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
_AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

_SPACES_REGION = os.environ.get('SPACES_REGION')
_SPACES_BUCKET = os.environ.get('SPACES_BUCKET')
_SPACES_ENDPOINT_URL = f'https://{_SPACES_REGION}.digitaloceanspaces.com'

_LOCAL_CACHE_DIR = os.environ.get('LOCAL_CACHE_DIR')

ML_ROOT = os.environ.get('ML_ROOT')
MODEL_ARTIFACT_ROOT = os.environ.get('MODEL_ARTIFACT_ROOT')
TRAINING_DATA_ROOT = os.environ.get('TRAINING_DATA_ROOT')


def fetch_file(path):
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name=_SPACES_REGION,
                            endpoint_url=_SPACES_ENDPOINT_URL,
                            aws_access_key_id=_AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=_AWS_SECRET_ACCESS_KEY)

    remote_path = os.path.join(path)
    local_path = os.path.join(_LOCAL_CACHE_DIR, path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    with open(local_path, 'wb') as write_file:
        client.download_fileobj(_SPACES_BUCKET, remote_path, write_file)

    read_file = open(local_path, 'rb')
    return read_file

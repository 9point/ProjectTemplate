import boto3
import os

_AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
_AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

_SPACES_REGION = os.environ.get('SPACES_REGION')
_SPACES_BUCKET = os.environ.get('SPACES_BUCKET')
_SPACES_ENDPOINT_URL = f'https://{_SPACES_REGION}.digitaloceanspaces.com'

_LOCAL_CACHE_DIR = os.environ.get('LOCAL_CACHE_DIR')


def _create_boto3_client():
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name=_SPACES_REGION,
                            endpoint_url=_SPACES_ENDPOINT_URL,
                            aws_access_key_id=_AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=_AWS_SECRET_ACCESS_KEY)
    return client


class s3_read:
    def __init__(self, path, mode='t'):
        self.path = path
        self.mode = mode
        self.file_handle = None

    def __enter__(self):
        client = _create_boto3_client()
        local_path = os.path.join(_LOCAL_CACHE_DIR, self.path)

        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        with open(local_path, 'wb') as write_file:
            client.download_fileobj(
                _SPACES_BUCKET, self.path, write_file)

        self.file_handle = open(local_path, f'r{self.mode}')
        return self.file_handle

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file_handle is not None:
            self.file_handle.close()


class s3_write:
    def __init__(self, path, mode='t'):
        self.path = path
        self.mode = mode
        self.file_handle = None

    def __enter__(self):
        local_path = os.path.join(_LOCAL_CACHE_DIR, self.path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        self.file_handle = open(local_path, f'w{self.mode}')
        return self.file_handle

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file_handle is None:
            return

        client = _create_boto3_client()
        local_path = os.path.join(_LOCAL_CACHE_DIR, self.path)

        with open(local_path, 'rb') as file:
            client.upload_fileobj(file, _SPACES_BUCKET, self.path)

        self.file_handle.close()
        self.file_handle = None


class s3_append:
    def __init__(self, path, mode='t'):
        self.path = path
        self.mode = mode
        self.file_handle = None

    def __enter__(self):
        local_path = os.path.join(_LOCAL_CACHE_DIR, self.path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        open_flag = f'a{self.mode}' if os.path.exists(
            local_path) else f'w{self.mode}'

        self.file_handle = open(local_path, open_flag)
        return self.file_handle

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file_handle is None:
            return

        client = _create_boto3_client()
        local_path = os.path.join(_LOCAL_CACHE_DIR, self.path)

        with open(local_path, 'rb') as file:
            client.upload_fileobj(file, _SPACES_BUCKET, self.path)

        self.file_handle.close()
        self.file_handle = None

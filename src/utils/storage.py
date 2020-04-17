import boto3
import os

_AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
_AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

_SPACES_REGION = os.environ.get('SPACES_REGION')
_SPACES_BUCKET = os.environ.get('SPACES_BUCKET')
_SPACES_ENDPOINT_URL = f'https://{_SPACES_REGION}.digitaloceanspaces.com'

_LOCAL_CACHE_DIR = os.environ.get('LOCAL_CACHE_DIR')


class S3File():
    def __init__(self, remote_path):
        self.remote_path = remote_path

    def _local_path(self):
        return os.path.join(_LOCAL_CACHE_DIR, self.remote_path)

    def _create_client(self):
        session = boto3.session.Session()
        client = session.client('s3',
                                region_name=_SPACES_REGION,
                                endpoint_url=_SPACES_ENDPOINT_URL,
                                aws_access_key_id=_AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=_AWS_SECRET_ACCESS_KEY)
        return client

    def _create_local_read_handle(self):
        client = self._create_client()
        local_path = self._local_path()
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        with open(local_path, 'wb') as write_file:
            client.download_fileobj(
                _SPACES_BUCKET, self.remote_path, write_file)

        read_file = open(local_path, 'rb')
        return read_file

    def _create_local_write_handle(self):
        local_path = self._local_path()
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        return open(local_path, 'wb')

    def read(self):
        # TODO: Use context manager.
        read_handle = self._create_local_read_handle()
        data = read_handle.read()
        read_handle.close()
        return data

    def readlines(self):
        # TODO: Use context manager.
        read_handle = self._create_local_read_handle()
        data = read_handle.readlines()
        read_handle.close()
        return data

    def write(self, data):
        client = self._create_client()

        # TODO: Use context manager.
        write_handle = self._create_local_write_handle()
        write_handle.write(data)
        write_handle.close()

        client.upload_file(self._local_path(),
                           _SPACES_BUCKET, self.remote_path)


# TODO: Add context manager.
def s3_open(path):
    return S3File(remote_path=path)

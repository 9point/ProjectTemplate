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

        self._local_file_handle = None
        self._is_prepared = False

    def sync(self):
        session = boto3.session.Session()
        client = session.client('s3',
                                region_name=_SPACES_REGION,
                                endpoint_url=_SPACES_ENDPOINT_URL,
                                aws_access_key_id=_AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=_AWS_SECRET_ACCESS_KEY)
        local_path = os.path.join(_LOCAL_CACHE_DIR, self.remote_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        with open(local_path, 'wb') as write_file:
            client.download_fileobj(
                _SPACES_BUCKET, self.remote_path, write_file)

        read_file = open(local_path, 'rb')

        self._local_file_handle = read_file
        self._is_prepared = True

    def read(self):
        assert(self._is_prepared)
        return self._local_file_handle.read()

    def readlines(self):
        assert(self._is_prepared)
        return self._local_file_handle.readlines()


# TODO: Add context manager here.
def s3_open(path):
    file = S3File(remote_path=path)
    file.sync()
    return file

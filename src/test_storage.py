import pandas
import torch

from utils.storage import s3_read, s3_write
from utils.task_mgr import define_task


@define_task(version="0.0.1")
def test_storage():
    with s3_read('ml/data/news_classifier/train_data.json') as file:
        data = pandas.read_json(file, orient='records')

    data = data.sample(frac=1)
    print(data.head())

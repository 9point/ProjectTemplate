import asyncio
import pandas as pd

from bow_classifier.pick_best_model import pick_best_model
from bow_classifier.train import train_model
from typing import Any, List
from utils import define
from utils.storage import s3_read, s3_write

TData = Any
THyperParams = Any
TModel = Any


@define.workflow(name="bow_classifier.build")
async def build(epochs: int, hyperparams: List[THyperParams]) -> TModel:
    with s3_read('ml/data/news_classifier/train_data.json') as file:
        data = pd.read_json(file, orient='records')
        data = data[:2000]
        data = data.sample(frac=1)

    training_execs = [
        train_model(data, epochs, batch_size=100, lr=hp['lr']) for hp in hyperparams]

    models = await asyncio.gather(*training_execs)

    print('Done training models')

    return await pick_best_model(data, models)

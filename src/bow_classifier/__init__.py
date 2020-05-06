import asyncio
import pandas as pd

from bow_classifier.train import main as _train
from typing import Any, List
from utils import define
from utils.storage import s3_read, s3_write
from utils.types import PyTorchModule

Data = Any
HyperParams = Any
Model = PyTorchModule


@define.workflow(name="bow_classifier.build")
async def build(epochs: int, hyperparams: List[HyperParams]) -> Model:
    print('running build')
    with s3_read('ml/data/news_classifier/train_data.json') as file:
        data = pd.read_json(file, orient='records')
        data = data[:2000]
        data = data.sample(frac=1)

    training_execs = [
        train_model(data, epochs, lr=hp['lr']) for hp in hyperparams]

    models = await asyncio.gather(*training_execs)
    return models[0]

    # return await pick_best_model(data, models)


@define.task(name="bow_classifier.train_model", version="0.0.1-dev")
def train_model(data: Data, epochs: int, lr: float) -> Model:
    print('running training model')
    return _train(data=data, epochs=epochs, batch_size=100, lr=lr)


@define.task(name="bow_classifier.pick_best_model", version="0.0.1-dev")
def pick_best_model(data: Data, models: List[PyTorchModule]) -> Model:
    return 'hello world'

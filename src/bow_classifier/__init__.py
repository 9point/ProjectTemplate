import asyncio

from bow_classifier.train import main as _train
from typing import Any, List
from utils import define
from utils.types import PyTorchModule

Data = Any
HyperParams = Any
Model = PyTorchModule


@define.workflow(name="bow_classifier.build")
async def build(data: Data, epochs: int, hyperparams: List[HyperParams]) -> Model:
    training_execs = [
        train_model(data, epochs, lr=hp['lr']) for hp in hyperparams]

    models = await asyncio.gather(training_execs)
    return await pick_best_model(data, models)


@define.task(name="bow_classifier.train_model", version="0.0.1-dev")
def train_model(data: Data, epochs: int, lr: float) -> Model:
    return _train(epochs=epochs, lr=lr)


@define.task(name="bow_classifier.pick_best_model", version="0.0.1-dev")
def pick_best_model(data: Data, models: List[PyTorchModule]) -> Model:
    return 'hello world'

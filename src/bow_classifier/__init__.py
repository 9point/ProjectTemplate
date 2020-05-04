import typing

from bow_classifier import _train
from utils.task_mgr import define_task, define_workflow, engine
from utils.task_mgr.types import PyTorchModule


@define_workflow(name="bow_classifier.build_and_eval")
def build_and_eval() -> PyTorchModule:
    build_exec = build()
    models = engine.wait(build_exec)
    return evaluate_models(models)


@define_workflow(name="bow_classifier.build")
def build() -> typing.List[PyTorchModule]:
    hyperparams = [
        {'lr': 0.1,  'batch_size': 100},
        {'lr': 0.01, 'batch_size': 100},
        {'lr': 0.1,  'batch_size': 10},
        {'lr': 0.01, 'batch_size': 10},
    ]

    training_execs = []
    for h in hyperparams:
        train_exec = train_model(epochs=20,
                                 batch_size=h['batch_size'],
                                 lr=h['lr'])

        training_execs.append(train_exec)

    return training_execs


@define_task(name="bow_classifier.train_model", version="0.0.1-dev")
def train_model(epochs: int, batch_size: int, lr: float) -> PyTorchModule:
    return _train.main(epochs=epochs,
                       batch_size=batch_size,
                       lr=lr)


@define_task(name="bow_classifier.evaluate_models", version="0.0.1-dev")
def evaluate_models(models: typing.List[PyTorchModule]) -> PyTorchModule:
    return 'hello world'

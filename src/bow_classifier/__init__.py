from bow_classifier import _train
from utils.task_mgr import define_task, define_workflow, engine
from utils.task_mgr.types import PyTorchModule

@define_workflow(name="bow_classifier.build")
def build():
    # Train 4 different hyper parameter settings
    # Pass the results of that training collectively to a test phase.
    # Pass the results of the test phase to a deploy phase.

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

    models = engine.wait_all(training_execs)
    best_model = engine.wait(evaluate_models(models=models))

    return deploy_model(model=best_model)

    # train_task()


@define_task(name="bow_classifier.train_model", version="0.0.1-dev")
def train_model(epochs: int, batch_size: int, lr: float) -> PyTorchModule:
    return _train.main(epochs=epochs,
                       batch_size=batch_size,
                       lr=lr)

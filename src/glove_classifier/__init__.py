from utils.task_mgr import define_task, define_workflow
from glove_classifier.train import main as train


@define_task(name="glove_classifier.train_model", version="0.0.1-dev")
def train_models():
    train()


@define_workflow(name="glove_classifier.build")
def build():
    train_models()


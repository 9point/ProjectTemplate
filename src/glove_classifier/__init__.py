from utils import define
from glove_classifier.train import main as train


@define.task(name="glove_classifier.train_model", version="0.0.1-dev")
def train_models():
    train()


@define.workflow(name="glove_classifier.build")
def build():
    train_models()

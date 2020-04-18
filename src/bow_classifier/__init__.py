from bow_classifier.train import main as train_task
from utils.task_mgr import define_workflow


@define_workflow(name="bow_classifier.train")
def train():
    train_task()

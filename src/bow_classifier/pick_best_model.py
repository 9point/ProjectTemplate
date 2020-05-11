import data_utils
import torch

from bow_classifier.model import Model
from data_utils import BOWEncoding, WordTokenDataset
from torch.utils.data import DataLoader
from typing import Any, List
from utils import define
from utils import logger as l

TData = Any
TModel = Any


@define.task(name="bow_classifier.pick_best_model", version="0.0.1-dev")
def pick_best_model(data: TData, models: List[TModel]) -> TModel:
    l.write('# Loading Data')

    encoding = BOWEncoding(data, min_word_freq=5)
    encoding.prepare()

    dataset = WordTokenDataset(data, encoding)
    dataset.prepare()

    valid_accuracies = []

    l.write('# Calculating Accuracies')

    samples = dataset[:]
    labels = samples.label

    for i, model in enumerate(models):
        l.write(f'Calculating accuracy for Model {i+1}')

        predictions = model.predict(samples)
        total = len(samples)
        correct = torch.sum(predictions == labels).item()

        accuracy = float(correct) / total
        valid_accuracies.append(accuracy)

    highest_accuracy = max(valid_accuracies)
    highest_accuracy_idx = valid_accuracies.index(highest_accuracy)
    best_model = models[highest_accuracy_idx]

    l.write(f'Best accuracy: {highest_accuracy*100:.02f}%')

    return best_model

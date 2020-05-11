import data_utils
import torch

from bow_classifier.model import Model
from data_utils import BOWEncoding, WordTokenDataset
from torch.utils.data import DataLoader
from typing import Any
from utils import define
from utils import logger as l

TData = Any
TModel = Any


@define.task(name="bow_classifier.train_model", version="0.0.1-dev")
def train_model(data: TData, epochs: int, batch_size: int, lr: float) -> TModel:
    l.write('# Setting Up Data')
    l.write(f'Training example count: {len(data)}')

    encoding = BOWEncoding(data, min_word_freq=5)
    encoding.prepare()

    dataset = WordTokenDataset(data, encoding)
    dataset.prepare()

    l.write('# Training')

    data_loader = DataLoader(dataset=dataset,
                             batch_size=batch_size,
                             shuffle=False,
                             collate_fn=data_utils.collate_samples)

    model = Model(vocab_size=encoding.vocab_size,
                  n_classes=encoding.n_classes())

    criterion = torch.nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        epoch_total_loss = 0

        epoch_progress = l.progressbar(key=f'epoch-{epoch}',
                                       name=f'Training Epoch {epoch + 1}')

        epoch_progress.show()

        batch_count = len(data_loader)

        for i, samples in enumerate(data_loader):
            optimizer.zero_grad()
            output = model(samples)
            loss = criterion(output, samples.label)
            loss.backward()
            optimizer.step()

            epoch_progress.set_progress((i+1) / float(batch_count))
            epoch_total_loss += loss.item()

        # Log the accuracy on predicting the first x examples.
        samples = dataset[:10000]
        predictions = model.predict(samples)
        labels = samples.label

        total = len(labels)
        correct = torch.sum(labels == predictions)

        l.write(f'Accuracy: {float(correct)/total*100:.02f}%.')
        l.write(f'Training Loss: {epoch_total_loss}')

    return model

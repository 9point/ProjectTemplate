import data_utils
import math
import numpy as np
import os
import pandas as pd
import string
import torch
import torch.nn as nn
import torch.nn.functional as F
import time

from bow_classifier.model import Model
from data_utils import BOWEncoding, WordTokenDataset
from datetime import datetime
from nltk.tokenize.regexp import WordPunctTokenizer
from torch.utils.data import DataLoader
from utils import logger as l
from utils.storage import s3_read, s3_write


def train(model, criterion, optimizer, dataset, data_loader, epochs):
    train_losses = []
    log_every = 1
    train_loss_estimator_size = 10000

    for epoch in range(epochs):
        losses = []

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

            losses.append(loss.item())
            epoch_progress.set_progress((i+1) / float(batch_count))

        train_loss = np.mean(losses)
        train_losses.append(train_loss)

        if (epoch + 1) % log_every == 0:
            train_loss_estimator_start = max(
                1, len(dataset) - train_loss_estimator_size)
            random_start = torch.randint(
                high=train_loss_estimator_start, size=(1,)).item()

            samples = dataset[random_start:(
                random_start+train_loss_estimator_size)]
            predictions = model.predict(samples)
            labels = samples.label

            total = len(labels)
            correct = torch.sum(labels == predictions)

            l.write(f'Accuracy: {float(correct)/total*100:.02f}%.')
            l.write(f'Training Loss: {train_loss.item()}\n')

    return train_losses


def main(data, epochs, batch_size, lr):
    l.write('# Setting Up Data')
    l.write(f'Training example count: {len(data)}')

    train_test_split = 0.95
    split_idx = math.floor(len(data) * train_test_split)

    train_data = data.iloc[0:split_idx]
    valid_data = data.iloc[split_idx:]

    encoding = BOWEncoding(data, min_word_freq=5)
    encoding.prepare()

    train_dataset = WordTokenDataset(train_data, encoding)
    train_dataset.prepare()

    valid_dataset = WordTokenDataset(valid_data, encoding)
    valid_dataset.prepare()

    l.write('# Training')

    data_loader = DataLoader(dataset=train_dataset,
                             batch_size=batch_size,
                             shuffle=False,
                             collate_fn=data_utils.collate_samples)

    model = Model(vocab_size=encoding.vocab_size,
                  n_classes=encoding.n_classes())

    criterion = torch.nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    train(model,
          criterion,
          optimizer,
          train_dataset,
          data_loader,
          epochs)

    return model

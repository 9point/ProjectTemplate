import data_utils
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from data_utils import WordEmbeddingEncoding, WordTokenDataset
from glove_classifier.Model import Model
from time import time
from torch.utils.data import Dataset, DataLoader
from utils import logger as l
from utils.storage import s3_read, s3_write

EPOCHS = 2


def train(model, criterion, optimizer, dataset, data_loader, epochs, log=True):
    train_losses = []

    for epoch in range(epochs):
        losses = []

        for i, samples in enumerate(data_loader):
            optimizer.zero_grad()
            output = model(samples)
            loss = criterion(output, samples.label)
            loss.backward()
            optimizer.step()

            losses.append(loss)

        train_loss = torch.mean(torch.stack(losses))
        train_losses.append(train_loss)

        if log and (epoch + 1) % 10 == 0:
            train_loss_estimator_size = 10000
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

            print(f'Epoch {epoch + 1}')
            print(f'Accuracy: {float(correct)/total*100:.02f}%.')
            print(f'Training Loss: {train_loss.item()}')
            print()

    return train_losses


def main():

    l.write('# Loading and Setting Up Data')

    l.write('Loading Training Data')
    with s3_read('ml/data/news_classifier/train_data.json') as file:
        data = pd.read_json(file, orient="records")
        data = data[:1000]

    l.write('Loading embeddings')

    with s3_read('ml/glove_embeddings/glove.6B.100d.txt') as file:
        embeddings = data_utils.load_embeddings(file, embedding_dim=100)

    l.write('Preparing data')

    train_test_split = 0.95
    split_idx = math.floor(len(data) * train_test_split)

    train_data = data.iloc[0:split_idx]
    valid_data = data.iloc[split_idx:]

    encoding = WordEmbeddingEncoding(data, embeddings)
    encoding.prepare()

    train_dataset = WordTokenDataset(train_data, encoding)
    train_dataset.prepare()

    valid_dataset = WordTokenDataset(valid_data, encoding)
    valid_dataset.prepare()

    print('# Training the Model')

    hyperparams_list = [
        {'weighting': 'uniform', 'lr': 0.001,  'batch_size': 100},
        {'weighting': 'uniform', 'lr': 0.01,   'batch_size': 100},
        {'weighting': 'uniform', 'lr': 0.001,  'batch_size': 50},
        {'weighting': 'uniform', 'lr': 0.01,   'batch_size': 50},
    ]

    models = []
    train_losses_list = []
    valid_losses = []

    accepted_tokens = {t for t in embeddings.index}

    for i, hyperparams in enumerate(hyperparams_list):
        l.write(f'Model {i+1} / {len(hyperparams_list)}')

        start_time = time()

        batch_size = hyperparams['batch_size']
        lr = hyperparams['lr']
        weighting = hyperparams['weighting']

        # 1. Setup Data Loader

        data_loader = DataLoader(dataset=train_dataset,
                                 batch_size=batch_size,
                                 shuffle=False,
                                 collate_fn=data_utils.collate_samples)

        # 2. Create the Model

        model = Model(embeddings=embeddings,
                      n_classes=encoding.n_classes(),
                      weighting=weighting)

        # 3. Setup Criterion and Optimizer

        criterion = torch.nn.CrossEntropyLoss()

        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

        # 4. Train the Model

        train_losses = train(model,
                             criterion,
                             optimizer,
                             train_dataset,
                             data_loader,
                             epochs=EPOCHS)

        # 5. Calculate Validation Loss

        with torch.no_grad():
            valid_samples = valid_dataset[:]

            outputs = model(valid_samples)

            valid_loss = criterion(outputs, valid_samples.label)
            valid_losses.append(valid_loss)

        end_time = time()

        models.append(model)
        train_losses_list.append(train_losses)

        l.write(f'Model completed in {(end_time - start_time)/60:.02f}m.\n')

    l.write('# Results')

    uniform_mask = [hp['weighting'] == 'uniform' for hp in hyperparams_list]

    models = [m for i, m in enumerate(models) if uniform_mask[i]]
    train_losses_list = [losses for i, losses in enumerate(
        train_losses_list) if uniform_mask[i]]
    valid_losses = [loss.item() for i, loss in enumerate(
        valid_losses) if uniform_mask[i]]

    best_model_idx = valid_losses.index(min(valid_losses))
    best_model = models[best_model_idx]

    l.write(f'Best Model: {best_model_idx+1}')
    l.write('Computing Model Accuracy...')

    samples = valid_dataset[:]

    predictions = best_model.predict(samples)

    total = len(samples.label)
    correct = torch.sum(predictions == samples.label)

    l.write(f'Accuracy of Model: {(float(correct) / total)*100:.02f}%.')

    l.write('Persisting Models...')

    with s3_write('ml/models/news_classifier/glove_model.torch', 'b') as file:
        torch.save(best_model.state_dict(), file)

    l.write('Done!')

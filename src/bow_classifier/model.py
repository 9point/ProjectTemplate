import torch
import torch.nn as nn

class Model(nn.Module):
    def __init__(self, vocab_size, n_classes):
        super(Model, self).__init__()
        self.vocab_size = vocab_size

        self.linear = nn.Linear(vocab_size, n_classes)

    def forward(self, samples):
        bow = samples.create_bow_matrix().type(torch.float32)
        output = self.linear(bow)
        return output

    def predict(self, samples):
        with torch.no_grad():
            outputs = self(samples)
            predictions = torch.argmax(outputs, axis=1)

        return predictions

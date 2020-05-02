import torch


class Model(torch.nn.Module):
    def __init__(self, embeddings, n_classes, weighting):
        super(Model, self).__init__()

        self.weighting = weighting

        torch_embeddings = torch.FloatTensor(embeddings.values)
        self.embedding_bag = torch.nn.EmbeddingBag.from_pretrained(
            torch_embeddings, mode='sum')
        self.linear = torch.nn.Linear(
            self.embedding_bag.embedding_dim, n_classes)

    def forward(self, samples):
        if self.weighting == 'tf_idf':
            weights = samples.create_tf_idf_weights()
        else:
            weights = samples.create_uniform_weights()

        x = self.embedding_bag(
            samples.sequence, samples.offset, per_sample_weights=weights)
        output = self.linear(x)
        return output

    def predict(self, samples):
        with torch.no_grad():
            outputs = self(samples)
            predictions = torch.argmax(outputs, axis=1)

        return predictions

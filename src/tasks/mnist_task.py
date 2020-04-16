from __future__ import print_function

import os
import time
import torch
import torch.distributed as dist
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from tensorboardX import SummaryWriter
from torchvision import datasets, transforms
from utils.task_mgr import define_task


WORLD_SIZE = int(os.environ.get('WORLD_SIZE', 1))

print('IMPORTING MNIST_TASK.py')


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.Linear(4*4*50, 500)
        self.fc2 = nn.Linear(500, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = x.view(-1, 4*4*50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


def train(args, model, device, train_loader, optimizer, epoch, writer):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args['log_interval'] == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tloss={:.4f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))
            niter = epoch * len(train_loader) + batch_idx
            writer.add_scalar('loss', loss.item(), niter)


def test(args, model, device, test_loader, writer, epoch):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            # sum up batch loss
            test_loss += F.nll_loss(output, target, reduction='sum').item()
            # get the index of the max log-probability
            pred = output.max(1, keepdim=True)[1]
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    print('\naccuracy={:.4f}\n'.format(
        float(correct) / len(test_loader.dataset)))
    writer.add_scalar('accuracy', float(correct) /
                      len(test_loader.dataset), epoch)


def should_distribute():
    return dist.is_available() and WORLD_SIZE > 1


def is_distributed():
    return dist.is_available() and dist.is_initialized()


@define_task(version="0.0.1")
def mnist():
    print('Running mnist...')

    # Training settings
    epochs = 1
    lr = 0.01
    momentum = 0.5
    seed = 1
    log_interval = 10
    save_model = False
    use_cuda = False

    args = {
        'epochs': epochs,
        'lr': lr,
        'momentum': momentum,
        'seed': seed,
        'log_interval': log_interval,
        'save_model': save_model,
        'use_cuda': use_cuda,
    }

    writer = SummaryWriter('logs')

    torch.manual_seed(1)

    device = torch.device("cuda" if use_cuda else "cpu")

    if should_distribute():
        print('Using distributed PyTorch with {} backend'.format(dist.Backend.GLOO))
        RANK = int(os.environ.get('RANK'))
        MASTER_PORT = os.environ.get('MASTER_PORT')
        MASTER_ADDR = os.environ.get('MASTER_ADDR')

        print(f'RANK={RANK}')
        print(f'MASTER_PORT={MASTER_PORT}')
        print(f'MASTER_ADDR={MASTER_ADDR}')
        print(f'WORLD_SIZE={WORLD_SIZE}')
        dist.init_process_group(backend=dist.Backend.GLOO,
                                rank=RANK,
                                world_size=WORLD_SIZE)

    batch_size = 64
    train_loader = torch.utils.data.DataLoader(
        datasets.MNIST('../data', train=True, download=True,
                       transform=transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ])), batch_size=batch_size, shuffle=False)
    test_loader = torch.utils.data.DataLoader(
        datasets.MNIST('../data', train=False, transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])), batch_size=batch_size, shuffle=False)

    model = Net().to(device)

    if is_distributed():
        Distributor = nn.parallel.DistributedDataParallelCPU
        model = Distributor(model)

    optimizer = optim.SGD(model.parameters(), lr=0.01,
                          momentum=args['momentum'])

    for epoch in range(1, epochs + 1):
        train(args, model, device, train_loader, optimizer, epoch, writer)
        test(args, model, device, test_loader, writer, epoch)

    if save_model:
        torch.save(model.state_dict(), "mnist_cnn.pt")

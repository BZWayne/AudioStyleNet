import torch.nn as nn
import torch

from torchvision import models as torch_models


# Pre-trained ResNet18
class PreTrainedResNet18(nn.Module):
    def __init__(self, sequence_length):
        super(PreTrainedResNet18, self).__init__()

        resnet = torch_models.resnet18(pretrained=True)
        num_ftrs = resnet.fc.in_features * sequence_length

        self.convolutions = nn.Sequential(
            resnet.conv1,
            resnet.bn1,
            resnet.relu,
            resnet.maxpool,
            resnet.layer1,
            resnet.layer2,
            resnet.layer3,
            resnet.layer4
        )

        for i, child in enumerate(self.convolutions.children()):
            for param in child.parameters():
                param.requires_grad = False

        self.avgpool = resnet.avgpool
        self.fc = nn.Linear(num_ftrs, 8)

    def forward(self, x):
        y = []
        for idx in range(0, x.shape[1], 3):
            y.append(self.convolutions(x[:, idx:idx + 3]))
        y = torch.cat(y, dim=1)
        y = self.avgpool(y)
        y = torch.flatten(y, 1)
        y = self.fc(y)

        return y


# RNN
class LandmarksLSTM(nn.Module):
    def __init__(self, window_size):
        super(LandmarksLSTM, self).__init__()

        self.rnn = nn.LSTM(68 * 2 * window_size, 128, 3, batch_first=True)
        self.fc = nn.Linear(128 * window_size, 8)

    def forward(self, x):
        # x.shape = [batch, sequence_length, 68 * 2 * window_size]
        out, hidden = self.rnn(x)
        out = torch.flatten(out, 1)
        out = self.fc(out)
        return out

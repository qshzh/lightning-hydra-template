from pl_bolts.models.self_supervised import CPCV2
from efficientnet_pytorch import EfficientNet
import torch.nn.functional as F
from torchvision import models
from torch import nn
import torch


class SimpleLinearMNIST(nn.Module):

    def __init__(self, config):
        super().__init__()

        # mnist images are (1, 28, 28) (channels, width, height)
        self.layer_1 = nn.Linear(28 * 28, config["lin1_size"])
        self.layer_2 = nn.Linear(config["lin1_size"], config["lin2_size"])
        self.layer_3 = nn.Linear(config["lin2_size"], config["lin3_size"])
        self.layer_4 = nn.Linear(config["lin3_size"], config["output_size"])

    def forward(self, x):
        batch_size, channels, width, height = x.size()

        # (b, 1, 28, 28) -> (b, 1*28*28)
        x = x.view(batch_size, -1)
        x = self.layer_1(x)
        x = F.relu(x)
        x = self.layer_2(x)
        x = F.relu(x)
        x = self.layer_3(x)
        x = F.relu(x)
        x = self.layer_4(x)

        return F.log_softmax(x, dim=1)


class EfficientNetPretrained(nn.Module):

    def __init__(self, config):
        super().__init__()

        self.model = EfficientNet.from_pretrained('efficientnet-b1')
        # self.model = EfficientNet.from_pretrained('efficientnet-b7')

        for param in self.model.parameters():
            param.requires_grad = True

        self.model._fc = nn.Sequential(
            nn.Linear(self.model._fc.in_features, config["lin1_size"]),
            nn.ReLU(),
            nn.Dropout(p=0.25),
            nn.Linear(config["lin1_size"], config["lin2_size"]),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(config["lin2_size"], config["output_size"]),
            nn.LogSoftmax(dim=1)
        )

    def forward(self, x):
        return self.model(x)


class ResnetPretrained(nn.Module):
    def __init__(self, config):
        super().__init__()

        self.model = models.resnet18(pretrained=True)

        for param in self.model.parameters():
            param.requires_grad = False

        self.model.fc = nn.Sequential(
            nn.Linear(self.model.fc.in_features, config["lin1_size"]),
            nn.ReLU(),
            nn.Dropout(p=0.15),
            nn.Linear(config["lin1_size"], config["output_size"]),
            nn.LogSoftmax(dim=1)
        )

    def forward(self, x):
        return self.model(x)


# this model doesn't work yet, we wait for lightinng-bolts patch
# class ResnetPretrainedUnsupervised(nn.Module):
#     """
#         Trained without labels on Imagenet.
#         Perhaps the features when trained without labels are much better for classification or other tasks.
#     """
#     def __init__(self, config):
#         super().__init__()
#
#         self.model = CPCV2(encoder='resnet18', pretrained='imagenet128').encoder
#         # self.model = CPCV2(encoder='resnet18', pretrained='stl10').encoder
#
#         for param in self.model.parameters():
#             param.requires_grad = False
#
#         self.model.fc = nn.Sequential(
#             nn.Linear(self.model.fc.in_features, config["lin1_size"]),
#             nn.ReLU(),
#             nn.Dropout(p=0.15),
#             nn.Linear(config["lin1_size"], config["output_size"]),
#             nn.LogSoftmax()
#         )
#
#     def forward(self, x):
#         return self.model(x)
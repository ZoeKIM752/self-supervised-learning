import torch.nn as nn
import torch
from torchvision import models, transforms
from torch.utils.data import DataLoader, Dataset
import torchvision

import torch.optim as optim
from torchlars import LARS

from BYOL import BYOL

from transform.simclr import TransformsSimCLR

#from validation import KNNValidation

import copy

EPOCHS = 100
image_size = 224
#image_size = 64
#image_size = 224
device = 'cuda'
BATCH = 512
#LR = 3e-4

vals_x = []
vals_y = []

if __name__ == '__main__':
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        #transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

    # train_dir = '/home/imlab/tiny-imagenet-200/train'
    # trainset = torchvision.datasets.ImageFolder(train_dir, transform=transforms.ToTensor())
    # trainloader = torch.utils.data.DataLoader(trainset, batch_size=BATCH, shuffle=True)


    transform = transforms.Compose(
        [transforms.ToTensor()])

    trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                            #download=True, transform=TransformsSimCLR(size=224))
                                            download=True, transform=transform)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=BATCH,
                                              shuffle=True, num_workers=2)

    #backbone = models.resnet50(pretrained=False)
    backbone = models.resnet18(pretrained=False)

    byol = BYOL(net=backbone, projection_size=256, projection_hidden_size=4096, image_size=image_size).to(device)
    byol = nn.DataParallel(byol)

    # optimizer = optim.SGD(byol.module.parameters(), lr=0.05 * BATCH / 256, momentum=0.9, weight_decay=1e-4)
    optimizer = optim.Adam(byol.module.parameters(), lr=3e-4)

    for step in range(EPOCHS):
        for i, data in enumerate(trainloader):
            x = data[0].to(device)
            loss = byol(x)

            print("[{}/{}] loss : {}".format(step,i,loss.mean()))

            optimizer.zero_grad()
            loss.mean().backward()
            optimizer.step()


        byol.module.EMA(step + 1, EPOCHS)

        if (step+1) % 10 == 0:
            torch.save(byol.module.state_dict(), 'byol_cifar10_{}_7.pth'.format(step+1))


    # for step in range(EPOCHS):
    #     for i, ((x1, x2), _) in enumerate(trainloader):
    #         x1 = x1.to(device)
    #         x2 = x2.to(device)
    #         loss = byol(x1,x2)

    #         print("[{}/{}] loss : {}".format(step,i,loss.mean()))

    #         optimizer.zero_grad()
    #         loss.mean().backward()
    #         optimizer.step()

    #     byol.module.EMA(step + 1, EPOCHS)

    #     if (step+1) % 10 == 0:
    #         torch.save(byol.module.state_dict(), 'byol_cifar10_{}_8.pth'.format(step+1))



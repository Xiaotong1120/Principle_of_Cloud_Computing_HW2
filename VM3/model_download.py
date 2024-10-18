import torch
model = torch.hub.load('chenyaofo/pytorch-cifar-models', 'cifar10_resnet20', pretrained=True)
model.eval()
torch.save(model.state_dict(), 'cifar10_resnet20.pth')
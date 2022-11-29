import gc
import torch
import torch.nn as nn
import time
import matplotlib.pyplot as plt
from torch.utils.data import Dataset
from torchvision import transforms
from tqdm import tqdm
from time import sleep
from resnet import ResNet50
from dataset import Fakeddit

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

num_classes = 2
num_epochs = 1
batch_size = 24
learning_rate = 0.01

train_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Lambda(lambda x: x.repeat(3, 1, 1) if x.shape[0] < 3 else x),  # convert grayscale to RGB
    transforms.Lambda(lambda x: x[:3] if x.shape[0] > 3 else x),  # convert 4 channels to 3
    transforms.RandomHorizontalFlip(p=0.5),
])

# Don't augment test data, only reshape
test_transforms = transforms.Compose([
    transforms.Resize((224, 224), max_size=224)
])

train_dir = './Fakeddit/train_reduced/'
label_file_train = './Fakeddit/train_reduced_more.csv'
train_data = Fakeddit(annotations_file=label_file_train, img_dir=train_dir,
                      transform=train_transforms)

valid_dir = './Fakeddit/validate_reduced/'
label_file_valid = './Fakeddit/valid_reduced_more.csv'
valid_data = Fakeddit(annotations_file=label_file_valid, img_dir=valid_dir,
                      transform=train_transforms)

test_dir = './Fakeddit/test_reduced/'
label_file_test = './Fakeddit/test_reduced_more.csv'
test_data = Fakeddit(annotations_file=label_file_test, img_dir=test_dir,
                     transform=test_transforms)

train_loader = torch.utils.data.DataLoader(
    train_data, batch_size=batch_size, shuffle=True)
valid_loader = torch.utils.data.DataLoader(
    valid_data, batch_size=batch_size, shuffle=True)

#model = ResNet(ResidualBlock, [3, 4, 6, 3]).to(device)
model = ResNet50(num_classes=2).to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, weight_decay=0.001, momentum=0.9)

# Train the model
total_step = len(train_loader)
accuracies_train = []
accuracies_validate = []
losses_train = []
losses_validate = []

start_time = time.time()

for epoch in range(num_epochs):
    with tqdm(enumerate(train_loader), unit="batch") as tepoch:
        for i, (images, labels) in tepoch:
            tepoch.set_description(f"Epoch {epoch}")
            # Move tensors to the configured device
            images = images.to(device)
            labels = labels.to(device)
            # Forward pass
            outputs = model(images)
            predictions = outputs.argmax(dim=1, keepdim=True).squeeze()
            correct = (predictions == labels).sum().item()
            accuracy = correct / batch_size
            accuracies_train.append(accuracy)
            loss = criterion(outputs, labels)
            losses_train.append(loss.item())
            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            tepoch.set_postfix(loss=loss.item(), accuracy=100. * accuracy)
            sleep(0.1)
            del images, labels, outputs
            torch.cuda.empty_cache()
            gc.collect()

    # Validation
    with torch.no_grad():
        total_correct = 0
        total = 0
        for images, labels in valid_loader:
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            losses_validate.append(loss.item())
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct = (predicted == labels).sum().item()
            total_correct += correct
            accuracy = correct / batch_size
            accuracies_validate.append(accuracy)
            del images, labels, outputs

        total_accuracy = 100 * total_correct / total
        print('Accuracy of the network on the validation images: {} %'.format(100 * total_accuracy))

print('Total execution time: {:.4f} minutes'
      .format((time.time() - start_time) / 60))

plt.figure(figsize=(10,5))
plt.title("Training and Validation Loss")
plt.plot(losses_validate,label="val")
plt.plot(losses_train,label="train")
plt.xlabel("iterations")
plt.ylabel("Loss")
plt.legend()
plt.show()

plt.figure(figsize=(10,5))
plt.title("Training and Validation accuracy")
plt.plot(accuracies_validate,label="val")
plt.plot(accuracies_train,label="train")
plt.xlabel("iterations")
plt.ylabel("accuracy")
plt.legend()
plt.show()
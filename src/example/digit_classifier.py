import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.softmax(x, dim=1)


def load_data(file_path: str) -> torch.Tensor:
    imgs = []

    with open(file_path, 'r') as f:
        for line in f.readlines():
            flatten_img = np.array(list(map(np.uint8, line.strip().split(' '))), dtype=np.uint8)
            img = flatten_img.reshape(1, 28, 28)
            imgs.append(img)

    imgs = np.array(imgs, dtype=np.uint8)

    return torch.tensor(imgs).float() / 255


def save_predicts(file_path: str, predicts: np.ndarray) -> None:
    with open(file_path, 'w+') as f:
        for idx, predict in enumerate(predicts):
            if idx != len(predicts) - 1:
                f.write(f'{str(predict)}\n')
            else:
                f.write(f'{str(predict)}')


if __name__ == '__main__':
    DATA_PATH = 'data.txt'
    MODEL_WEIGHTS_PATH = 'weights.pth'
    PREDICTS_PATH = 'predicts.txt'

    imgs = load_data(DATA_PATH)
    model = Net()
    model.load_state_dict(torch.load(MODEL_WEIGHTS_PATH))
    model.eval()

    logits = model(imgs)
    predicts = logits.argmax(dim=1).numpy()

    save_predicts(PREDICTS_PATH, predicts)

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
import glob
import os

class SimpleLstm(nn.Module):
    def __init__(self, input_size = 6, hidden_size=32, num_layers=1, num_classes=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out
    


def load_mjff_train_data(train_folder):
    all_x, all_y = [], []
    files = glob.glob(os.path.join(train_folder, "*.csv"))

    print(f"found {len(files)} csv files in {train_folder}")

    for f in files:
        df = pd.read_csv(f)
        if "Valid" in df.columns:
            df = df[df["Valid"] == 1]
        if not all(col in df.columns for col in ["AccV", "AccML", "AccAP", "GyroV", "GyroML", "GyroAP", "FoG"]):
            continue
        x = df[["AccV", "AccML", "AccAP", "GyroV", "GyroML", "GyroAP"]].values

        y = df["FoG"].values
        seq_len = 128

        for i in range(0, len(x)-seq_len, seq_len):
            window = x[i:i+seq_len]
            label = int(y[i:i+seq_len].max())
            all_x.append(window)
            all_y.append(label)

    x = np.stack(all_x)
    y = np.array(all_y)

    print(f"{x.shape[0]} windows, shape={x.shape}")

    return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.long)


def train_lstm(train_folder):
    x, y = load_mjff_train_data(train_folder)

    dataset = TensorDataset(x, y)
    loader = DataLoader(dataset, batch_size=64, shuffle=True)

    model = SimpleLstm()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(dataset, batch_size=64, shuffle=True)

    for epoch in range(5):
        for xb, yb in loader:
            optimizer.zero_grad()
            preds = model(xb)
            loss = criterion(preds, yb)
            loss.backward()
            optimizer.step()
        print(f"{epoch + 1} - loss {loss.item():.4f}")

    
    torch.save(model.state_dict(), "lstm_model.pt")
    print("")


    return model



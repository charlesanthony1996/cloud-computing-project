import os
import torch
from models import SimpleLstm, LightLstm, load_mjff_train_data

import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# config variables
train_folder = "./defog"
out_dir = "../models"
seq_len = 128
batch_size = 64
epochs = 5
lr = 1e-3

os.makedirs(out_dir, exist_ok=True)

# load the data
x, y = load_mjff_train_data(train_folder)

dataset = TensorDataset(x, y)
loader = DataLoader(dataset, batch_size= batch_size, shuffle=True)

# train simple lstm model
simple_model = SimpleLstm(input_size = 3)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(simple_model.parameters(), lr = lr)

for epoch in range(epochs):
    for xb, yb in loader:
        optimizer.zero_grad()
        preds = simple_model(xb)
        loss = criterion(preds, yb)
        loss.backward()
        optimizer.step()
    print(f"[Simple] Epoch {epoch+1}/{epochs} loss={loss.item():.4f}")

simple_path = os.path.join(out_dir, "simple_lstm_model.pt")
torch.save(simple_model.state_dict(), simple_path)
print(f"saved {simple_path}")

# train the light model
light_model = LightLstm(input_size = 3)
optimizer = torch.optim.Adam(light_model.parameters(), lr = lr)

for epoch in range(epochs):
    for xb, yb in loader:
        optimizer.zero_grad()
        preds = light_model(xb)
        loss = criterion(preds, yb)
        loss.backward()
        optimizer.step()
    print(f"[light] epoch {epoch+1}/{epochs} loss = {loss.item():.4f}")


light_path = os.path.join(out_dir, "light_lstm_model.pt")
torch.save(light_model.state_dict(), light_path)

print("local training is complete")
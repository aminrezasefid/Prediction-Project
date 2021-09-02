import math
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Tuple
import pandas as pd
from torch_geometric.data import Data

val_batches=72
def trainer(data: Data, model, epochs=100, lr=0.001, lr_discount=0.2, batch_size=9):
    print("Starting training ...")
    matches = data.matches.append(data.data_val, ignore_index=True)
    for i in range(0, matches.shape[0], batch_size):
        val_evaluate(data, model, matches.iloc[i:i + val_batches * batch_size])
        train_start_point = max(0, i - 40 * batch_size)
        train(data,model,matches.iloc[train_start_point:i + batch_size],epochs,lr,batch_size)
        print("T:{}, train_loss:{:.5f}, train_acc:{:.5f}, val_loss={:.5f}, val_acc={:.5f}"
              .format(int(i / batch_size),
                      data.train_loss,
                      data.train_accuracy,
                      data.val_loss,
                      data.val_accuracy))
                      

def val_evaluate(data: Data, model: torch.nn.Module, matches):
    criterion = nn.NLLLoss()  # weight=torch.tensor([1.6,1.95,1])
    predicted, label, outputs = get_predictions(data, model, matches)
    loss = criterion(outputs, label).item()

    correct = int((predicted == label).sum().item())
    data.val_accuracy=(float(correct) / matches.shape[0])
    data.val_loss=loss

def get_predictions(data: Data, model: torch.nn.Module, matches) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    outputs, label = get_probabilities(data, model, matches)
    _, predicted = torch.max(torch.exp(outputs.data), 1)
    return predicted, label, outputs

def get_probabilities(data, model, matches):
    model.eval()
    home, away, label = torch.from_numpy(matches['home_team'].values.astype('int64')), \
                        torch.from_numpy(matches['away_team'].values.astype('int64')), \
                        torch.from_numpy(matches['lwd'].values.astype('int64').reshape(-1, ))
    with torch.no_grad():
        outputs = model(data, home, away)
    #model.train() #inja ro bepors hatman
    return outputs, label

def train(data: Data, model: torch.nn.Module, matches,
               epochs:int = 100, lr: int = 0.0001, batch_size:int = 9, print_info: bool = False):
    criterion = nn.NLLLoss()  # weight=torch.tensor([1.6,1.95,1])
    optimizer = optim.Adam(model.parameters(), lr=lr)
    running_loss = []
    running_accuracy = []
    for epoch in range(epochs):
        acc = 0
        loss_value = 0.0
        optimizer.zero_grad()
        for j in range(0, matches.shape[0], batch_size):
            home, away, result = torch.from_numpy(matches.iloc[j:j + batch_size]['home_team'].values.astype('int64')), \
                                 torch.from_numpy(matches.iloc[j:j + batch_size]['away_team'].values.astype('int64')), \
                                 torch.from_numpy(matches.iloc[j:j + batch_size]['lwd'].values.astype('int64').reshape(-1, ))
            outputs = model(data, home, away)
            loss = criterion(outputs, result)
            loss.backward()
            optimizer.step()
            #inja nabayad seda zade beshe: optimizer.zero_grad() 
            loss_value += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            correct = int((predicted == result).sum().item())
            running_accuracy.append(correct)
            acc += correct

            update_edge_time(data, home, away, result)
            update_edge_index(data)
            calculate_edge_weight(data)

        if print_info:
            print("Epoch:{}, train_loss:{:.5f}, train_acc:{:.5f}"
                  .format(epoch, loss_value, acc / (matches.shape[0])))
        running_loss.append(loss_value)
    data.train_loss=sum(running_loss) / ((matches.shape[0] / batch_size) * epochs)
    data.train_accuracy=sum(running_accuracy) / (matches.shape[0] * epochs)
import numpy as np
import torch
from torch_geometric.data import Data
from tqdm import tqdm

from DataTransformer import DataTransformer
from utils import *
Edge_type = {
    'loose': 1,
    'player': 2,
    'past':3
}

class Dataset:
    def __init__(self, filename):
        self.filename = filename
    def process(self):
        dt = DataTransformer(self.filename)
        data_train, data_val, data_test = dt.prepare_data()
        x = torch.ones(dt.n_nodes).reshape(-1, 1)
        data = Data(
                edge_index=torch.tensor([]).reshape(2,-1).long(),
                edge_type=torch.tensor([]).reshape(-1).long(),
                n_nodes=dt.n_nodes,
                nodes=dt.nodes,
                x=x,
                matches=data_train,
                data_val=data_val,
                data_test=data_test,
                train_loss=[],
                train_accuracy=[],
                val_loss=[],
                val_accuracy=[],
            )
        return data
    
    


from DataTransformer import DataTransformer
from Trainer import *
from GNNModel import GNNModel
from Dataset import Dataset

def run_gnn_model(filename, lr=0.0001):
    dataset = Dataset(filename=filename)
    data_list = dataset.process() # load and process all the data
    epochs = [30] # number of initial epochs
    
    model = GNNModel(data_list.n_nodes)
    print("GNN model, data {}")
    trainer(data_list, model, epochs[0],lr=lr, batch_size=9)

dataset_filename="Data/PL_scraped_ord.csv"
run_gnn_model(dataset_filename)

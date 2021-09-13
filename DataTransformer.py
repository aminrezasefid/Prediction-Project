import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import torch
from utils import *

usecols=['home_team', 'away_team', 'result', 'home_lineup', 'away_lineup']
class DataTransformer:
    def __init__(self, filename: str):
        self.label_encoder = LabelEncoder()
        self.filename = filename
        self.data = None
        self.n_teams=None
        self.read_data()
        self.data = self.clean_data(self.data)
        self.N = self.data.shape[0]

    def read_data(self):
        """Read the data from csv with correct data types."""
        #self.data = pd.read_csv(self.filename, header=None, names=names,dtype=dict(zip(names, [int] + [str] * 4 + [int] * 3 + [str] * 2)))
        self.data=pd.read_csv(self.filename, encoding='latin-1', usecols=usecols)

    def clean_data(self,data, convert_to_numpy=False) :
        """Add a column to transform result of the match into int, """
        corrupted = self.data.loc[pd.isna(self.data['away_lineup']) | pd.isna(self.data['home_lineup'])]
        data = self.data.drop(corrupted.index, axis=0)
        conditions = [
            (data['result'] == 'home'),
            (data['result'] == 'tie'),
            (data['result'] == 'away')]
        choices = [2,1,0]
        data['lwd'] = np.select(conditions, choices)
        if usecols[-1] != 'lwd':
            usecols.append('lwd')
        return data
    def prepare_data(self):
        data=self.data
        
        separator_val = int(data.__len__() * 0.8)
        separator_test = int(data.__len__() * 0.9)
        # separator_test_final = int(int(data.__len__() * 0.9))
        data_train = pd.DataFrame(data=data[:separator_val], columns=usecols)
        data_val = pd.DataFrame(data=data[separator_val:separator_test], columns=usecols)
        data_test = pd.DataFrame(data=data[separator_test:], columns=usecols)
        # data_test_final = pd.DataFrame(data=data[separator_test_final:], columns=names)
        self.data_train = data_train
        self.data_val = data_val
        self.data_test = data_test
        self.nodes,self.n_nodes=nodes_gen(self.data)
        return data_train, data_val, data_test

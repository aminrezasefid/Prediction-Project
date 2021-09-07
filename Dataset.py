import numpy as np
import torch
from torch_geometric.data import Data
from tqdm import tqdm

from DataTransformer import DataTransformer

Edge_type = {
    'loose': 1,
    'player': 2,
    'past':3
}

class Dataset:
    def __init__(self, filename):
        self.filename = filename
        self.week=0

    def update_graph(self,data,home_players,home_features,home,away_features,away_players,away,result):
        self.week+=1
        curr_factor=10*len(str(self.week))
        prev_factor=10*len(str(self.week-1))

        #win loose graph
        winning_team = np.array([]).astype('int64')
        losing_team = np.array([]).astype('int64')
        # home won
        winning_team = np.append(winning_team, home[np.where(result == 2)[0]])
        losing_team = np.append(losing_team, away[np.where(result == 2)[0]])
        # away won
        winning_team = np.append(winning_team, away[np.where(result == 0)[0]])
        losing_team = np.append(losing_team, home[np.where(result == 0)[0]])
        # draw
        winning_team = np.append(winning_team, home[np.where(result == 1)[0]])
        winning_team = np.append(winning_team, away[np.where(result == 1)[0]])
        losing_team = np.append(losing_team, away[np.where(result == 1)[0]])
        losing_team = np.append(losing_team, home[np.where(result == 1)[0]])
        team_edge=torch.tensor((losing_team*curr_factor+self.week,winning_team*curr_factor+self.week))
        edge_type=Edge_type['loose']
        team_type=torch.tensor([edge_type]*team_edge.shape[1])

        #player graph
        player_type=torch.tensor([]).reshape(-1).long()
        player_edge=torch.tensor([]).reshape(2,-1).long()
        for i in range(home.shape[0]):
            for j in range(home_players[i].shape[0]):
                player_edge.cat(home_players[i][j])


        #timing_graph
        time_edge=torch.tensor([]).reshape(2,-1).long()
        time_type=torch.tensor([]).reshape(-1).long()
        if self.week >1:
            edge_type=Edge_type['past']
            time_home_team_edge=torch.tensor((home*prev_factor+self.week-1,home*curr_factor+self.week))
            time_away_team_edge=torch.tensor((away*prev_factor+self.week-1,away*curr_factor+self.week))
            time_edge=torch.cat((time_edge,time_home_team_edge,time_away_team_edge),dim=1)

            home_players_list=home_players.reshape(-1)
            away_players_list=away_players.reshape(-1)
            time_home_player_edge=torch.tensor((home_players_list*prev_factor+self.week-1,home_players_list*curr_factor+self.week))
            time_away_player_edge=torch.tensor((away_players_list*prev_factor+self.week-1,away_players_list*curr_factor+self.week))
            time_edge=torch.cat((time_edge,time_home_player_edge,time_away_player_edge),dim=1)
            time_type=torch.cat((time_type,torch.tensor([edge_type]*time_edge.shape[1])),dim=0)
        
        data.edge_index=torch.cat((data.edge_index,team_edge,player_edge,time_edge),dim=1)
        data.edge_type=torch.cat((data.edge_type,team_type,player_type,time_type),dim=0)






    def process(self):
        dt = DataTransformer(self.filename)
        data_train, data_val, data_test, data_test_final, teams_enc = dt.prepare_data(data=dt)
        n_teams = len(teams_enc['teams'].values)
        x = torch.ones(dt.n_teams).reshape(-1, 1)
        data = Data(
                edge_index=torch.tensor([]).reshape(2,-1).long(),
                edge_type=torch.tensor([]).reshape(1,-1).long(),
                x=x,
                matches=data_train,
                n_teams=n_teams,
                data_val=data_val,
                data_test=data_test,
                data_test_final=data_test_final,
                train_loss=[],
                train_accuracy=[],
                val_loss=[],
                val_accuracy=[],
                teams_enc=teams_enc
            )
        return data
    

    


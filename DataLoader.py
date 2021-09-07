import numpy as np


def update_graph(data,home_features,home,away_features,away,result):
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

    data.edge_index=

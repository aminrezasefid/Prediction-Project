import torch
WON = 1
LOST_TO = 2
TIED_WITH = 3
PLAYED_IN = 4
USED = 5
BEFORE = 6
AFTER = 7

def remove_redundancy(players):
    new_players = list()
    for player in players:
        if 'Own' in player:
        # print(player)
            player = player.replace('Own', '')
        if 'Pen. Scored' in player:
        # print(player)
            player = player.replace('Pen. Scored', '')
        if 'Pen. Score' in player:
        # print(player)
            player = player.replace('Pen. Score', '')
        if 'Own' in player or 'Scored' in player or '.' in player or 'Score' in player:
            print(player)
        #SHOULD NOT PRINT IF CODE IS CORRECT
        else:
            new_players.append(player.strip())
    return new_players

def get_home_away_indices(df,nodes):
    home_teams=[]
    away_teams = []
    result =torch.from_numpy( df['lwd'].values.astype('int64').reshape(-1, ))
    for index, (h_team, a_team, _,_,_,_) in df.iterrows():
        home_teams.append(nodes[f'{h_team}*{index}'])
        away_teams.append(nodes[f'{a_team}*{index}'])

    return torch.tensor(home_teams),torch.tensor(away_teams),result
def nodes_gen(df):
    from collections import OrderedDict as od
    nodes = dict()
    node_counter = 1

    for index, (h_team, a_team, result, h_lineup, a_lineup,_) in df.iterrows():
        home_players = h_lineup[:-4].split(' - ')
        away_players = a_lineup[:-4].split(' - ')

        home_players = remove_redundancy(home_players)
        away_players = remove_redundancy(away_players)
        home_teams=[]
        away_teams = []
        for player_index, player in enumerate(home_players):
            nodes[f'{player}@{index}'] = node_counter
            node_counter += 1
        for player_index, player in enumerate(away_players):
            nodes[f'{player}@{index}'] = node_counter
            node_counter += 1

        nodes[f'{h_team}*{index}'] = node_counter
        home_teams.append(node_counter)
        node_counter += 1

        nodes[f'{a_team}*{index}'] = node_counter
        away_teams.append(node_counter)
        node_counter += 1

    return od(sorted(nodes.items())),node_counter-1
def home_won_gen(df,nodes):
    home_winning_matches = df.loc[df['result'] == 'home']
    home_winners = home_winning_matches['home_team']
    away_losers = home_winning_matches['away_team']

    winning_hashes = list()
    losing_hashes = list()

    for home, away, match in zip(home_winners, away_losers, home_winners.index):
        winning_hashes.append(f'{home}*{match}')
        losing_hashes.append(f'{away}*{match}')

    winning_nodes = list()
    losing_nodes = list()

    for winner, loser in zip(winning_hashes, losing_hashes):
        winning_nodes.append(nodes[winner]) 
        losing_nodes.append(nodes[loser])

    won_edges = torch.tensor(
        [

        losing_nodes,winning_nodes
        ]
    )

    lost_edges = torch.tensor(
        [
        winning_nodes,losing_nodes
        ]
    )

    won_edge_types = torch.ones(won_edges.shape[1]) * WON
    lost_edge_types = torch.ones(lost_edges.shape[1]) * LOST_TO 

    return won_edges, won_edge_types, lost_edges, lost_edge_types
def away_won_gen(df,nodes):

    away_winning_matches = df.loc[df['result'] == 'away']
    away_winners = away_winning_matches['away_team']
    home_losers = away_winning_matches['home_team']

    winning_hashes = list()
    losing_hashes = list()

    for home, away, match in zip(home_losers, away_winners, away_winners.index):
        winning_hashes.append(f'{away}*{match}')
        losing_hashes.append(f'{home}*{match}')

    winning_nodes = list()
    losing_nodes = list()

    for winner, loser in zip(winning_hashes, losing_hashes):
        winning_nodes.append(nodes[winner]) 
        losing_nodes.append(nodes[loser])

    won_edges = torch.tensor(
        [
        losing_nodes,winning_nodes
        ]
    )

    lost_edges = torch.tensor(
        [
        winning_nodes,losing_nodes
        ]
    )
    
    won_edge_types = torch.ones(won_edges.shape[1]) * WON
    lost_edge_types = torch.ones(lost_edges.shape[1]) * LOST_TO 
    
    return won_edges, won_edge_types, lost_edges, lost_edge_types
def tied_gen(df,nodes):
    tied_matches = df.loc[df['result'] == 'tie']
    home_teams = tied_matches['home_team']
    away_teams = tied_matches['away_team']

    home_hashes = list()
    away_hashes = list()

    for home, away, match in zip(home_teams, away_teams, away_teams.index):
        away_hashes.append(f'{away}*{match}')
        home_hashes.append(f'{home}*{match}')

    home_nodes = list()
    away_nodes = list()

    for home, away in zip(home_hashes, away_hashes):
        home_nodes.append(nodes[home]) 
        away_nodes.append(nodes[away])

    home_tied_edges = torch.tensor(
        [
        home_nodes,
        away_nodes
        ]
    )

    away_tied_edges = torch.tensor(
        [
        away_nodes,
        home_nodes
        ]
    )

    home_tied_edge_types = torch.ones(home_tied_edges.shape[1]) * TIED_WITH
    away_tied_edge_types = torch.ones(away_tied_edges.shape[1]) * TIED_WITH

    return home_tied_edges, home_tied_edge_types, away_tied_edges, away_tied_edge_types

def played_used_gen(df,nodes):

  team_nodes = list()
  player_nodes = list()

  for index, (h_team, a_team, result, h_lineup, a_lineup,_) in df.iterrows():
    home_players = h_lineup[:-4].split(' - ')
    away_players = a_lineup[:-4].split(' - ')

    home_players = remove_redundancy(home_players)
    away_players = remove_redundancy(away_players)

    for home_player, away_player in zip(home_players, away_players):
      player_nodes.append(nodes[f'{home_player}@{index}'])
      team_nodes.append(nodes[f'{h_team}*{index}'])
      player_nodes.append(nodes[f'{away_player}@{index}'])
      team_nodes.append(nodes[f'{a_team}*{index}'])

  played_in_edges = torch.tensor(
      [
       player_nodes,
       team_nodes
      ]
  )

  played_in_edge_types = torch.ones(played_in_edges.shape[1]) * PLAYED_IN

  used_edges = torch.tensor(
      [
       team_nodes,
       player_nodes
      ]
  ) 

  used_edge_types = torch.ones(used_edges.shape[1]) * USED

  return played_in_edges, played_in_edge_types, used_edges, used_edge_types

def players_before_after_gen(df,nodes):
  keys = list(nodes.keys())
  player_match_hashes = list(filter(lambda key: ('@' in key), keys))

  sorted_hashes = sorted(
      player_match_hashes,
      key= lambda w: (w.split('@')[0], int(w.split('@')[1]))
  )

  # print(s)

  r = {k:v for v, k in nodes.items()}

  before_nodes = list()
  after_nodes = list()

  for index, hash in enumerate(sorted_hashes):
    player, match = hash.split('@')
    before_node = nodes[hash]
    try:
      after_node = nodes[sorted_hashes[index+1]]
      if r[before_node].split('@')[0] == r[after_node].split('@')[0]:
        before_nodes.append(before_node)
        after_nodes.append(after_node)
        
    except:
      pass
  before_edges = torch.tensor(
      [
      before_nodes,
      after_nodes
      ]
  )

  before_edge_types = torch.ones(before_edges.shape[1]) * BEFORE

  after_edges = torch.tensor(
      [
      after_nodes,
      before_nodes
      ]
  )

  after_edge_types = torch.ones(after_edges.shape[1]) * AFTER

  return before_edges, before_edge_types, after_edges, after_edge_types

def edge_generator(data,df):
        nodes,_ = nodes_gen(df)
        edge_index=torch.tensor([]).reshape(2,-1).long()
        edge_type=torch.tensor([]).reshape(-1).long()
        home_win_edges,home_win_edge_types,_,_= home_won_gen(df,nodes)
        away_win_edges,away_win_edge_types,_,_= away_won_gen(df,nodes)
        home_tied_edges, home_tied_edge_types, away_tied_edges, away_tied_edge_types=tied_gen(df,nodes)
        played_in_edges, played_in_edge_types,_,_=played_used_gen(df,nodes)
        before_edges, before_edge_types, _, _= players_before_after_gen(df,nodes)
        edge_index=torch.cat((home_win_edges,away_win_edges,home_tied_edges,away_tied_edges,played_in_edges,before_edges),dim=1)
        edge_type=torch.cat((home_win_edge_types,away_win_edge_types,home_tied_edge_types,away_tied_edge_types,played_in_edge_types,before_edge_types),dim=0)
        data.edge_index=torch.cat((data.edge_index,edge_index),dim=1)
        data.edge_type=torch.cat((data.edge_type,edge_type),dim=0)
        return edge_index, edge_type
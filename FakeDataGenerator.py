import pandas as pd
import numpy as np
import random
from scipy.special import expit


#constants
template_file_name_EPL = "PL_scraped_ord.csv"
template_file_name_Thesis = "GER1_all.csv"
output_file_name_EPL = "FakeData_EPL.csv"
output_file_name_Thesis = "FakeData_Thesis.csv"
output_column_names = ['match_id', 'country', 'league', 'season', 'week', 'date', 'home_team', 'away_team', 'home_goal', 'away_goal', 'result', 'home_lineup', 'away_lineup']

player_strength_vec_size = 15
maximum_possible_goals = 5
noise_amount = 0
fake_season_count = 5
linear_transform_vector = 0

#Randomizer Objects
PlayerStrength_rnd = np.random.default_rng(2021)
random.seed(2020)


out_data_ours = []
out_data_thesis = []



def maptorange(src_min, src_max, dest_min, dest_max, x):
    return dest_min + (((dest_max - dest_min)/(src_max - src_min)) * (x - src_min))


def remove_redundancy(players):
  new_players = list()

  for player in players:
    if 'Own' in player:
      player = player.replace('Own', '')
    if 'Pen. Scored' in player:
      player = player.replace('Pen. Scored', '')
    if 'Pen. Score' in player:
      player = player.replace('Pen. Score', '')
    if 'Own' in player or 'Scored' in player or '.' in player or 'Score' in player:
      print(player)
      #SHOULD NOT PRINT IF CODE IS CORRECT
    else:
      new_players.append(player.strip())
  return new_players





#Reads the real data and collects player and team names
def CollectTeamsandPlayers():
    real_data = pd.read_csv(
        template_file_name_EPL, 
        encoding='latin-1', 
        usecols= ['home_team', 'home_lineup']
    )
    corrupted = real_data.loc[pd.isna(real_data['home_lineup'])]
    real_data = real_data.drop(corrupted.index, axis=0).reset_index(drop= True)

    Teams = set(real_data['home_team'].loc[real_data.index[:380]])
    Team_lineups = list(real_data['home_lineup'].loc[real_data.index[:380]])
    Players = list()
    
    for l in Team_lineups:
        tmp = l.strip(' -').split(' - ')
        Players.extend(remove_redundancy(tmp))
    
    return sorted(Teams), sorted(set(Players))


#Gives each player a random strength vector
def RandomizePlayerStrength(Players):
    player_dict = {}
    for p in Players:
        player_dict[p] = PlayerStrength_rnd.random(player_strength_vec_size) * 10
    return player_dict


#Distributes Players between teams randomly
def DistributePlayers(Teams, Players):
    random.shuffle(Teams)
    team_count = len(Teams)
    player_count = len(Players)
    team_size_base = player_count // team_count
    teams_dict = {}
    for t in Teams:
        team_size = team_size_base + 1 if player_count % team_size_base != 0 else team_size_base
        chosen = random.sample(Players, team_size)
        Players = list(filter(lambda p: p not in chosen, Players))
        player_count = len(Players)
        teams_dict[t] = chosen
    
    return teams_dict





class season:
    def __init__(self, Teams, Players, season_number):
        self.week_count = (len(Teams) - 1)*2
        self.season_number = season_number
        self.Players = Players
        self.Teams = DistributePlayers(Teams, list(Players)) #Teams is a dict from now on {'teamname': player list}
        self.Weeks = [] #list of season weeks. Each member is a list of games in that week. each sub member = tuple(home, away)
        for i in range(self.week_count):
            self.Weeks.append([])
        
        
    def CreateGameWeeks(self):
        team_list = list(self.Teams)

        #Round1
        random.shuffle(team_list)
        row1 = team_list[:(len(self.Teams)//2)]
        row2 = team_list[(len(self.Teams)//2):]
        row2.reverse()
        for w in range(self.week_count//2):
            return_week_idx = random.randrange(self.week_count//2, self.week_count)
            while len(self.Weeks[return_week_idx]) >= len(self.Teams)//2:
                    return_week_idx = return_week_idx + 1
                    if return_week_idx >= self.week_count:
                        return_week_idx = self.week_count//2
            for t1, t2 in zip(row1, row2):
                if w%2: t1,t2 = t2,t1
                self.Weeks[w].append((t1, t2))
                self.Weeks[return_week_idx].append((t2, t1))

                            
            row2.append(row1.pop())
            row1.insert(1, row2.pop(0))


        #Round2
        
        # for t in team_list:
        #     for t2 in team_list:
        #         if t != t2:
        #             while True:
        #                 week_idx = random.randrange(0, self.week_count)
        #                 if (t2, t) not in self.Weeks[week_idx]:
        #                     self.Weeks[week_idx].append((t, t2))
        #                     break


    def PlayGames(self):
        for week in range(self.week_count):
            for game in self.Weeks[week]:
                home = game[0]
                home_lineup = random.sample(self.Teams[home], 11)
                away = game[1]
                away_lineup = random.sample(self.Teams[away], 11)

                home_strength = np.zeros(player_strength_vec_size)
                away_strength = np.zeros(player_strength_vec_size)
                for p in home_lineup:
                    home_strength += self.Players[p]
                for p in away_lineup:
                    away_strength += self.Players[p]

                # home_strength = home_strength / 11
                # away_strength = away_strength / 11

                home_strength = np.multiply(home_strength, linear_transform_vector)
                away_strength = np.multiply(away_strength, linear_transform_vector)


                home_strength = float(np.sum(home_strength)) 
                away_strength = float(np.sum(away_strength)) 




                home_strength += PlayerStrength_rnd.uniform(-(home_strength*noise_amount), home_strength*noise_amount)
                away_strength += PlayerStrength_rnd.uniform(-(away_strength*noise_amount), away_strength*noise_amount)

                

                out_data_ours.append([
                    '0', 'fake', 'fake', self.season_number, week+1, '0', home, away,
                    home_strength, away_strength, '0',
                    ' - '.join(home_lineup), ' - '.join(away_lineup)
                ])

            
                out_data_thesis.append([
                    self.season_number, 'fake', '0', home, away, home_strength, away_strength, 0, '0', 'fake' 
                ])


def main():
    # epl_template = pd.read_csv(template_file_name_EPL, encoding='latin-1').columns
    # print(epl_template)
    # print(epl_template.get_loc('away_fouls') - epl_template.get_loc('home_score') + 1)



    Teams, Players = CollectTeamsandPlayers()
    Players = RandomizePlayerStrength(Players) #Players is a dict from now on {'playername': strength vector}
    global linear_transform_vector
    linear_transform_vector = PlayerStrength_rnd.random(player_strength_vec_size)


    with open(output_file_name_EPL, 'w') as outfile:
        outfile.write('')
    with open(output_file_name_Thesis, 'w') as outfile:
        outfile.write('')

    for s in range(fake_season_count):
        s1 = season(Teams, Players, 1990+s)
        s1.CreateGameWeeks()
        s1.PlayGames()
        print(f'season: {s} created.')

    
    df_ours = pd.DataFrame(out_data_ours, columns= output_column_names)
    max_st = max(df_ours['home_goal'].max(), df_ours['away_goal'].max())
    min_st = min(df_ours['home_goal'].min(), df_ours['away_goal'].min())


    df_ours.loc[:, 'home_goal'] = round(maptorange(min_st, max_st, 0, 5, df_ours['home_goal']))
    df_ours.loc[:, 'away_goal'] = round(maptorange(min_st, max_st, 0, 5, df_ours['away_goal']))
    df_ours.loc[:, 'result'] =  df_ours['home_goal'] - df_ours['away_goal']
    df_ours.loc[:, 'result'] = df_ours['result'].apply(lambda z: 'home' if z > 0 else 'tie' if z == 0 else 'away')


    df_thesis = pd.DataFrame(out_data_thesis)
    df_thesis.loc[:, 5] = round(maptorange(min_st, max_st, 0, 5, df_thesis[5]))
    df_thesis.loc[:, 6] = round(maptorange(min_st, max_st, 0, 5, df_thesis[6]))
    df_thesis.loc[:, 7] = df_thesis[5] - df_thesis[6]
    df_thesis.loc[:, 8] = df_thesis[7].apply(lambda z: 'W' if z > 0 else 'D' if z == 0 else 'L')

    df_ours.to_csv(output_file_name_EPL, index= False)
    df_thesis.to_csv(output_file_name_Thesis,index= False, header= False)

    return df_ours, df_thesis

    
    
if __name__ == "__main__":
    main()


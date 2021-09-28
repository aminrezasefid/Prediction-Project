from typing import final
import pandas as pd
import numpy as np
import random
from collections import deque



#constants
template_file_name_EPL = "PL_scraped_ord.csv"
template_file_name_Thesis = "GER1_all.csv"
output_file_name_EPL = "FakeData_EPL.csv"
output_file_name_Thesis = "FakeData_Thesis.csv"
player_strength_vec_size = 15
fake_season_count = 20
draw_threshhold = 10

#Randomizer Objects
PlayerStrength_rnd = np.random.default_rng(2021)
random.seed(2020)





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
    real_data = real_data.drop(corrupted.index, axis=0)

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
        self.Weeks = [] #list of season weeks. Each member is a list of games in that week. each member = tuple(home, away)
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

                match_result = home_strength - away_strength
                match_result = float(np.sum(match_result))
                final_result_Thesis = ''
                final_result_EPL = ''
                if match_result > draw_threshhold:
                    final_result_EPL = 'home'
                    final_result_Thesis = 'W'
                elif match_result <= draw_threshhold and match_result >= (-1)*draw_threshhold:
                    final_result_EPL = 'tie'
                    final_result_Thesis = 'D'
                else:
                    final_result_EPL = 'away'
                    final_result_Thesis = 'L'
                out_str_epl = f"0,{self.season_number},{week+1}," + \
                            '0,'*6 + \
                            f"{home},{away}," + \
                            '0,'*16 + \
                            f"{final_result_EPL}," + \
                            '0,'*32 + \
                            f"{' - '.join(home_lineup)} - ,{' - '.join(away_lineup)} - \n"
                with open(output_file_name_EPL, 'a') as outfile:
                    outfile.write(out_str_epl)

                out_str_Thesis = f"{self.season_number},EPL,0,{home},{away},{'0,'*3}{final_result_Thesis},England\n"
                with open(output_file_name_Thesis, 'a') as outfile:
                        outfile.write(out_str_Thesis)
                




if __name__ == "__main__":

    # epl_template = pd.read_csv(template_file_name_EPL, encoding='latin-1').columns
    # print(epl_template)
    # print(epl_template.get_loc('away_fouls') - epl_template.get_loc('home_score') + 1)



    Teams, Players = CollectTeamsandPlayers()
    Players = RandomizePlayerStrength(Players) #Players is a dict from now on {'playername': strength vector}
    
    with open(output_file_name_EPL, 'w') as outfile:
        epl_template = list(pd.read_csv(template_file_name_EPL, encoding='latin-1').columns)
        outfile.write(','.join(epl_template) + '\n')
    with open(output_file_name_Thesis, 'w') as outfile:
        outfile.write('')

    for s in range(fake_season_count):
        s1 = season(Teams, Players, 1990+s)
        s1.CreateGameWeeks()
        s1.PlayGames()
        print(f'season: {s} created.')

    # a = ('Blackburn Rovers', 'Tottenham Hotspur')
    # print('Blackburn Rovers' in a)
    
    


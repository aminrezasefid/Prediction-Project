import pandas as pd
import numpy as np
import random
from collections import deque



#constants
template_file_name = "PL_scraped_ord.csv"
output_file_name = "FakeData.csv"
player_strength_vec_size = 15
fake_season_count = 20

#Randomizer Objects
PlayerStrength_rnd = np.random.default_rng(2021)
random.seed(2020)





#Reads the real data and collects player and team names
def ReadTemplate():
    real_data = pd.read_csv(
        template_file_name, 
        encoding='latin-1', 
        usecols= ['home_team', 'home_lineup']
    )
    Teams = set(real_data['home_team'].loc[real_data.index[:380]])
    Team_lineups = list(real_data['home_lineup'].loc[real_data.index[:380]])
    Players = set()
    
    for l in Team_lineups:
        tmp = l.replace(' ', '').strip('-').split('-')
        for p in tmp:
            Players.add(p)
            

    
    return sorted(Teams), sorted(Players)


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
    def __init__(self, Teams, Players):
        self.week_count = (len(Teams) - 1)*2
        self.Teams = DistributePlayers(Teams, list(Players)) #Teams is a dict from now on {'teamname': player list}
        self.Weeks = [] #list of season weeks. Each member is a list of games in that week. each member = tuple(home, away)
        for i in range(self.week_count):
            self.Weeks.append([])
        self.CreateGameWeeks()
        
    
        
    def CreateGameWeeks(self):
        team_list = list(self.Teams)

        #Round1
        random.shuffle(team_list)
        row1 = team_list[:(len(self.Teams)//2)]
        row2 = team_list[(len(self.Teams)//2):]
        for w in range(self.week_count//2):
            for t1, t2 in zip(row1, row2):
                self.Weeks[w].append((t1, t2))
                self.Weeks[random.randrange(self.week_count/2, self.week_count)].append((t2, t1))
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
                            




if __name__ == "__main__":
    Teams, Players = ReadTemplate()
    Players = RandomizePlayerStrength(Players) #Players is a dict from now on {'playername': strength vector}
    

    s1 = season(Teams, Players)
    


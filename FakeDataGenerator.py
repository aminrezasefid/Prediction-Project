import pandas as pd
import numpy as np
import random
from collections import deque



#constants
template_file_name = "PL_scraped_ord.csv"
output_file_name = "FakeData.csv"
player_strength_vec_size = 15
fake_season_count = 20
draw_threshhold = 10

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
                final_result = ''
                if match_result > draw_threshhold:
                    final_result = 'W'
                elif match_result <= draw_threshhold and match_result >= (-1)*draw_threshhold:
                    final_result = 'D'
                else:
                    final_result = 'L'
                out_str = f"{self.season_number},{week+1},{home},{away},{final_result},{'-'.join(home_lineup)},{'-'.join(away_lineup)}\n"
                with open(output_file_name, 'a') as outfile:
                    outfile.write(out_str)
                




if __name__ == "__main__":
    Teams, Players = ReadTemplate()
    Players = RandomizePlayerStrength(Players) #Players is a dict from now on {'playername': strength vector}
    
    with open(output_file_name, 'w') as outfile:
        outfile.write("Season_number,Week,home_team,away_team,result,home_lineup,away_lineup\n")

    for s in range(fake_season_count):
        s1 = season(Teams, Players, 1990+s)
        s1.CreateGameWeeks()
        s1.PlayGames()
        print(f'season: {s} created.')

    # a = ('Blackburn Rovers', 'Tottenham Hotspur')
    # print('Blackburn Rovers' in a)
    
    


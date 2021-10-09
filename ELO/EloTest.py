from DataTransformer import DataTransformer
nteams=18
class Team:
    def __lt__(self,x):
        return self.rating>x.rating
    def __init__(self,name,rating=1000):
        self.name = name
        self.rating = rating
    def update(self,opp,score):
        Eself=1.0//(1.0+10**((opp.rating-self.rating)/400.0))
        newSelfRating=self.rating+nteams*42*(score-Eself)
        self.rating=newSelfRating
        
dt = DataTransformer("../Data/GER1_all.csv")
teams=dt.teams
Eteams={}
for team in teams:
    Eteams[team]=Team(team)
for i,game in dt.data.iterrows():
        home=game['home_team']
        away=game['away_team']
        homepoint=0
        awaypoint=0
        if game['result']=="W":
            homepoint=3
            awaypoint=0
        elif game['result']=="D":
            homepoint=1
            awaypoint=1
        else: 
            homepoint=0
            awaypoint=3
        elo1=Eteams[home]
        elo2=Eteams[away]

        elo1.update(elo2,homepoint)
        elo2.update(elo1,awaypoint)
sortedgteams={k: v for k, v in sorted(Eteams.items(), key=lambda item: item[1])}
print("elo score:")
for team in sortedgteams:
    print(f"new Rating Deviation for  {team}:" + str(sortedgteams[team].rating))

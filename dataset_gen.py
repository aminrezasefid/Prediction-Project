import pandas as pd
import requests
from os import getcwd


url = "https://raw.githubusercontent.com/jokecamp/FootballData/master/EPL%202011-2019/PL_scraped_ord.csv"
current_directory = getcwd()
filename = './Data/dataset.txt'

req = requests.get(url)
if req.status_code == 200:
  with open(filename, 'wb') as fp:
    fp.write(req.content)


df = pd.read_csv(filename, encoding='latin-1', usecols=['home_team', 'away_team', 'result', 'home_lineup', 'away_lineup'])

remove_list = list()

#remove matches where either the home or the away lineup is missing
for id, (h, a) in enumerate(zip(df['home_lineup'], df['away_lineup'])):
  if pd.isna(a) or pd.isna(h):
    remove_list.append(id)

df = df.drop(remove_list, axis=0)

df.to_csv('./Data/dataset.txt', index=False)


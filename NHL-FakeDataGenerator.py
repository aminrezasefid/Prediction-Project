import numpy as np


np.random.seed(2021)

def match_result(result):
  if result > 0: return 'W'
  elif result == 0: return 'D'
  else: return 'L'

GAMES_PER_REG_SEASON = 868
N_TEAMS = 32
PLAYERS_PER_TEAM = 12
DIM = 64

rng = 1

# 32 teams, each team has 11 players, each player is embedding in a 64-dimensional vector
players_strengths = np.random.randn(N_TEAMS, PLAYERS_PER_TEAM, DIM) * rng

with open('./Data/players-per-team.csv', 'w') as players_per_team_fp:
  players_per_team_fp.write('team-index,[players]\n')
  for team in range(N_TEAMS):
    player_indcs = list(range(team * PLAYERS_PER_TEAM + 1, team * PLAYERS_PER_TEAM + PLAYERS_PER_TEAM + 1))
    players = [team + 1, player_indcs]
    players_per_team_fp.write(
        ','.join(map(str, players))
    )
    players_per_team_fp.write('\n')


with open('./Data/player_strengths.csv', 'w') as players_strengths_fp:
  players_strengths_fp.write('player,[strength]\n')
  for team in range(N_TEAMS):
    for player in range(PLAYERS_PER_TEAM):
      player_strength = list(players_strengths[team][player])
      players_strengths_fp.write(
          ','.join(map(str, [team*PLAYERS_PER_TEAM+player+1, player_strength]))
      )
      players_strengths_fp.write('\n')

#w1 and b1 are for player strength aggregation
w1 = np.random.randn(DIM, DIM) * rng
b1 = np.random.randn(DIM, 1) * rng

#w2 and b2 are for match prediction
w2 = np.random.randn(1, DIM) * rng
b2 = np.random.randn(1, 1) * rng

with open('./Data/parameters.csv', 'w') as params_fp:
  params_fp.write('[w1], [w2], b1, b2\n')
  params = [list(np.ravel(w1)), list(np.ravel(w2)), b1[0], b2[0]]
  params_fp.write(
    ','.join(map(str, params))
  )
  params_fp.write('\n')

team_games = {team+1:0 for team in range(N_TEAMS)}

with open('./Data/match-results.csv', 'w') as  match_results_fp:
  match_results_fp.write('team1-[team1-players],team2,[team2-pkayers],goal-difference,team1-result\n')
  for game in range(GAMES_PER_REG_SEASON):
    team1, team2 = tuple(np.random.permutation([team for team in range(N_TEAMS)])[:2])
    team_games[team1+1] += 1
    team_games[team2+1] += 1
    team1_players = np.random.permutation([player for player in range(PLAYERS_PER_TEAM)])[:6]
    team2_players = np.random.permutation([player for player in range(PLAYERS_PER_TEAM)])[:6]

    team1_strength = np.matmul(
        w1,
        np.sum(players_strengths[team1][team1_players].T, axis=1, keepdims=True)
    ) + b1

    team2_strength = np.matmul(
        w1,
        np.sum(players_strengths[team2][team2_players].T, axis=1, keepdims=True)
    ) + b1

    result = np.matmul(
        w2,
        team1_strength - team2_strength
        
    ) + b2

    f = np.vectorize(lambda z: z if -5 <= z <= 5 else 0 )
    result = f(result)
    result = np.round(result, 0)
    
    players1 = [team1 * PLAYERS_PER_TEAM + player + 1 for player in team1_players]
    players2 = [team2 * PLAYERS_PER_TEAM + player + 1 for player in team2_players]
    
    
    match = [team1+1, players1, team2+1, players2, int(result.item()), match_result(result.item())]
    match_results_fp.write(
        ','.join(map(str, match))
    )
    match_results_fp.write('\n')

for team, games_played in team_games.items():
  print(f'Team {team} played {games_played} games')
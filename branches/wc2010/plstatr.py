import os, re, time

def print_stats(teams, min_games = 20, file = None):
  i = 1
  stats_dir = "stats"
  if file: f = open(os.path.join(stats_dir, file), 'w')
  for team in teams:
    if team[3] >= min_games:
      line = "%3d. %-22s %5.3f %2d" % (i, team[1], team[0], team[3])
      if file: f.write("%s\n" % line)
      #print line
      i += 1
  if file: f.close()

def compare_teams(x, y):
  if x[0] != y[0]:
    return -cmp(x[0], y[0])
  elif x[3] != y[3]:
    return -cmp(x[3], y[3])
  else:
    return cmp(x[1], y[1])

def calculate_stats(dic, reverse_sort = False):
  stats = []
  stats_home = []
  stats_away = []
  for team in dic:
    home_total = dic[team][0]
    home_games = dic[team][1]
    away_total = dic[team][2]
    away_games = dic[team][3]
    total = home_total + away_total
    games = home_games + away_games
    if home_games == 0:
      home_avg = 0
    else:
      home_avg = float(home_total) / home_games
    if away_games == 0:
      away_avg = 0
    else:
      away_avg = float(away_total) / away_games
    total_avg = float(total) / games
    stats.append([total_avg, team, total, games])
    if home_games > 0:
      stats_home.append([home_avg, team, home_total, home_games])
    if away_games > 0:
      stats_away.append([away_avg, team, away_total, away_games])
    
  stats.sort(compare_teams, reverse = reverse_sort)
  stats_home.sort(compare_teams, reverse = reverse_sort)
  stats_away.sort(compare_teams, reverse = reverse_sort)

  return stats, stats_home, stats_away

start_dir = 'archive'
resources_dir = 'resources'
stats_file_pattern = re.compile(".*_stats.txt$")
stats_line_pattern = re.compile("^.\d\.\s(?P<home>.*)\sv\s(?P<away>.*)(?P<goals_home>\d+)\s+-\s+(?P<goals_away>\d+)\s+(?P<total>\d+)\s+(?P<avg>\d\.\d{3})$")
stats = {}
prediction_success = {}
team_success = {}
goals_scored = {}
goals_conceded = {}
result_frequency = {}
total_games = 0

time.clock()

syn_file = open(os.path.join(resources_dir, 'team_synonyms.txt'), 'r')
synonyms = syn_file.readlines()
syn_file.close()
syn_list = [s[:-1].split(';') for s in synonyms]

for d in os.walk(start_dir):
  if d[0].find('Euro') > -1 or d[0].find('World') > -1:
    continue
  for f in d[2]:
    found = stats_file_pattern.search(f)
    if found:
      stats_file = os.path.join(d[0], found.group())
      file = open(stats_file, 'r')
      l = file.readlines()
      for line in l:
        line_match = stats_line_pattern.search(line)
        if line_match:
          # get team names
          home = line_match.group('home')
          away = line_match.group('away').strip()
          for syn in syn_list:
            if home == syn[0]:
              home = syn[1]
            if away == syn[0]:
              away = syn[1]
          # prediction success
          avg = float(line_match.group('avg'))
          stats[line[:-1]] = avg
          if prediction_success.has_key(home):
            prediction_success[home][0] += avg
            prediction_success[home][1] += 1
          else:
            prediction_success[home] = [avg, 1, 0, 0]
          if prediction_success.has_key(away):
            prediction_success[away][2] += avg
            prediction_success[away][3] += 1
          else:
            prediction_success[away] = [0, 0, avg, 1]
          # team success
          goals_home = int(line_match.group('goals_home'))
          goals_away = int(line_match.group('goals_away'))
          if goals_home > goals_away:
            points = [3, 0]
          elif goals_home < goals_away:
            points = [0, 3]
          else:
            points = [1, 1]
          if team_success.has_key(home):
            team_success[home][0] += points[0]
            team_success[home][1] += 1
          else:
            team_success[home] = [points[0], 1, 0, 0]
          if team_success.has_key(away):
            team_success[away][2] += points[1]
            team_success[away][3] += 1
          else:
            team_success[away] = [0, 0, points[1], 1]
          # goals scored / conceded at home
          if goals_scored.has_key(home):
            goals_scored[home][0] += goals_home # scored at home
            goals_scored[home][1] += 1
          else:
            goals_scored[home] = [goals_home, 1, 0, 0]
          if goals_conceded.has_key(home):
            goals_conceded[home][0] += goals_away # conceded at home
            goals_conceded[home][1] += 1
          else:
            goals_conceded[home] = [goals_away, 1, 0, 0]
          # goals scored / conceded away
          if goals_scored.has_key(away):
            goals_scored[away][2] += goals_away # scored away
            goals_scored[away][3] += 1
          else:
            goals_scored[away] = [0, 0, goals_away, 1]
          if goals_conceded.has_key(away):
            goals_conceded[away][2] += goals_home # conceded away
            goals_conceded[away][3] += 1
          else:
            goals_conceded[away] = [0, 0, goals_home, 1]
          total_games += 1
      file.close()

print "Total games predicted:", total_games

# most predictable games
games = map(None, stats.values(), stats.keys())
games.sort(reverse = True)

i = 0
while games[i][0] > 3:
  print games[i][1]
  i += 1

prediction_success_total, prediction_success_home, prediction_success_away = calculate_stats(prediction_success)
team_success_total, team_success_home, team_success_away = calculate_stats(team_success)
goals_scored_total, goals_scored_home, goals_scored_away = calculate_stats(goals_scored)
goals_conceded_total, goals_conceded_home, goals_conceded_away = calculate_stats(goals_conceded, True)

# stats for teams with min_games games played
print_stats(prediction_success_total, file = "plstatr_prediction_success.txt")
print_stats(prediction_success_home, 10, "plstatr_prediction_success_home.txt")
print_stats(prediction_success_away, 10, "plstatr_prediction_success_away.txt")
print_stats(team_success_total, file = "plstatr_team_success.txt")
print_stats(team_success_home, 10, "plstatr_team_success_home.txt")
print_stats(team_success_away, 10, "plstatr_team_success_away.txt")
print_stats(goals_scored_total, file = "plstatr_goals_scored.txt")
print_stats(goals_scored_home, 10, "plstatr_goals_scored_home.txt")
print_stats(goals_scored_away, 10, "plstatr_goals_scored_away.txt")
print_stats(goals_conceded_total, file = "plstatr_goals_conceded.txt")
print_stats(goals_conceded_home, 10, "plstatr_goals_conceded_home.txt")
print_stats(goals_conceded_away, 10, "plstatr_goals_conceded_away.txt")

# stats for all teams
print_stats(prediction_success_total, 1, file = "plstatr_prediction_success_all.txt")
print_stats(prediction_success_home, 1, "plstatr_prediction_success_home_all.txt")
print_stats(prediction_success_away, 1, "plstatr_prediction_success_away_all.txt")
print_stats(team_success_total, 1, file = "plstatr_team_success_all.txt")
print_stats(team_success_home, 1, "plstatr_team_success_home_all.txt")
print_stats(team_success_away, 1, "plstatr_team_success_away_all.txt")
print_stats(goals_scored_total, 1, file = "plstatr_goals_scored_all.txt")
print_stats(goals_scored_home, 1, "plstatr_goals_scored_home_all.txt")
print_stats(goals_scored_away, 1, "plstatr_goals_scored_away_all.txt")
print_stats(goals_conceded_total, 1, file = "plstatr_goals_conceded_all.txt")
print_stats(goals_conceded_home, 1, "plstatr_goals_conceded_home_all.txt")
print_stats(goals_conceded_away, 1, "plstatr_goals_conceded_away_all.txt")

print "Completed in %ss" % time.clock()

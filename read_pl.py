import os, re, string, struct, time
from pysqlite2 import dbapi2 as sqlite

def read_games(filename, team_syn_list, cur):
  games_line_pattern = re.compile("(?P<home_team>^.*)\sv\s(?P<away_team>.*$)")
  f = open(filename, 'r')
  l = f.readlines()
  team_list = []
  for line in l:
    found_game = games_line_pattern.search(line)
    if found_game:
      home = found_game.group('home_team')
      away = found_game.group('away_team')
      for syn in team_syn_list:
        if home == syn[0]:
          home = syn[1]
        if away == syn[0]:
          away = syn[1]
      team_list.append(home)
      team_list.append(away)
      cur.execute('SELECT * FROM team WHERE name = ?', (home, ))
      if not cur.fetchall():
        cur.execute('INSERT INTO team(id, name, country_id) VALUES(NULL, ?, 0)', (home, ))
      cur.execute('SELECT * FROM team WHERE name = ?', (away, ))
      if not cur.fetchall():
        cur.execute('INSERT INTO team(id, name, country_id) VALUES(NULL, ?, 0)', (away, ))
  f.close()
  return len(l), team_list

def read_results(filename, n):
  f = open(filename, 'rb')
  result_list = []
  for i in range(0, n):
    try:
      (home, away) = struct.unpack('hh', f.read(4))
      result_list.append(home)
      result_list.append(away)
    except: break
  f.close()
  return result_list

def read_predictions(filename, n, game_id_list, player_syn_list, cur):
  f = open(filename, 'rb')
  while f:
    try: 
      if filename.find('2002-03') > -1: # 2002-03 season had a longer name field
        name = struct.unpack('32s', f.read(32))[0]
      else:
        name = struct.unpack('31s', f.read(31))[0]
      name = name[:name.index('\0')]
      for syn in player_syn_list:
        if name == syn[0]:
          name = syn[1]
      cur.execute('SELECT * FROM player WHERE name = ?', (name, ))
      row = cur.fetchone()
      if row == None:
        cur.execute('INSERT INTO player(id, name) VALUES(NULL, ?)', (name, ))
        player_id = cur.lastrowid
      else:
        player_id = row[0]
    except: break
    for i in range(0, n):
      try:
        (home, away) = struct.unpack('hh', f.read(4))
        if (home == 9 and away == 9): # no prediction made (old format: 9 - 9, new format: -1 - -1)
          home = -1
          away = -1
        # calculate points
        if (home == -1 and away == -1):
          home_points, away_points = -1, -1
        else:
          if home > away:
            home_points, away_points = 3, 0
          elif home == away:
            home_points, away_points = 1, 1
          else:
            home_points, away_points = 0, 3
        cur.execute('SELECT home_result, away_result FROM game WHERE id = ?', (game_id_list[i], ))
        result = cur.fetchone()
        points_scored = 0
        if result[0] == 9 and result[1] == 9:
          points_scored = 0
        elif home == -1 and away == -1:
          points_scored = 0
        elif home == result[0] and away == result[1]:
          points_scored = 4
        elif home == away and result[0] == result[1]:
          if (home - result[0] == 1) or (result[0] - home == 1):
            points_scored = 3
          else:
            points_scored = 2
        elif (home - away) == (result[0] - result[1]):
          points_scored = 3
        elif (home > away and result[0] > result[1]) or (home < away and result[0] < result[1]):
          points_scored = 2
        cur.execute('INSERT INTO prediction(id, player_id, game_id, home, away, home_points, away_points, points) VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)',
                    (player_id, game_id_list[i], home, away, home_points, away_points, points_scored))
      except: break
  f.close()

def load_synonyms(path):
  syn_file = open(path, 'r')
  synonyms = syn_file.readlines()
  syn_file.close()
  syn_list = [s[:-1].split(';') for s in synonyms]
  return syn_list

start_dir = 'archive'
resources_dir = 'resources'
games_file_pattern = re.compile("(?P<round>\d+)_games.txt$")
results_file_pattern = re.compile("(?P<round>\d+)_results.txt$")
predictions_file_pattern = re.compile("(?P<round>\d+)_predictions.txt$")
num_games = {}

team_syn_list = load_synonyms(os.path.join(resources_dir, 'team_synonyms.txt'))
player_syn_list = load_synonyms(os.path.join(resources_dir, 'player_synonyms.txt'))

con = sqlite.connect('agcmpl.db')
cur = con.cursor()
time.clock()

for root, dirs, files in os.walk(start_dir):
  if root.find('Euro') > -1 or root.find('World') > -1:
    continue
  season = root[root.rfind('\\') + 1:]
  for f in files:
    found_games = games_file_pattern.search(f)
    if found_games:
      n, team_list = read_games(os.path.join(root, f), team_syn_list, cur)
      r = found_games.group('round')
      if num_games.has_key(season): # new round
        num_games[season][r] = n
      else: # new season
        num_games[season] = {r: n}
        cur.execute('SELECT * FROM season WHERE id = ?', (season, ))
        if not cur.fetchall():
          cur.execute('INSERT INTO season(id) VALUES(?)', (season, ))
      cur.execute('SELECT * FROM round WHERE season_id = ? AND id = ?', (season, r))
      if not cur.fetchall():
        cur.execute('INSERT INTO round(season_id, id) VALUES(?, ?)', (season, r))
      # read results
      f = f[:3] + 'results.txt'
      results_file = os.path.join(root, f)
      if not os.path.exists(results_file):
        print 'Missing file %s' % results_file
        continue
      result_list = read_results(results_file, num_games[season][r])
      game_id_list = []
      for i in range(0, n):
        cur.execute('SELECT id FROM team WHERE name = ?', (team_list[i * 2], ))
        home_id = cur.fetchall()[0][0]
        cur.execute('SELECT id FROM team WHERE name = ?', (team_list[i * 2 + 1], ))
        away_id = cur.fetchall()[0][0]
        home_result = result_list[i * 2]
        away_result = result_list[i * 2 + 1]
        if home_result > away_result:
          home_points, away_points = 3, 0
        elif home_result == away_result:
          home_points, away_points = 1, 1
        else:
          home_points, away_points = 0, 3
        cur.execute("""INSERT INTO game(id, round_id, season_id, home_id, away_id, home_result, away_result, home_points, away_points)
                          VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (r, season, home_id, away_id, home_result, away_result, home_points, away_points))
        game_id_list.append(cur.lastrowid)
      # read predictions
      f = f[:3] + 'predictions.txt'
      read_predictions(os.path.join(root, f), num_games[season][r], game_id_list, player_syn_list, cur)

uefa_members_file = open(os.path.join(resources_dir, "uefa_members.txt"), "r")
uefa_members_codes_file = open(os.path.join(resources_dir, "uefa_members_codes.txt"), "r")
teams_by_country_file = open(os.path.join(resources_dir, "teams_by_country.txt"), "r")
i = 0
for country in uefa_members_file:
  i += 1
  country_teams = teams_by_country_file.readline().strip().split(",")
  code = uefa_members_codes_file.readline().strip()
  cur.execute("""INSERT INTO country(id, name, code)
                  VALUES(?, ?, ?)""", (i, country.strip(), code))
  for team in country_teams:
    cur.execute('SELECT id FROM team WHERE name = ?', (team, ))
    row = cur.fetchone()
    if row != None:
      team_id = row[0]
      cur.execute("""UPDATE team
                        SET country_id = ?
                        WHERE id = ?""", (i, team_id))

print "Completed in %ss" % time.clock()

teams_by_country_file.close()
uefa_members_codes_file.close()
uefa_members_file.close()

con.commit()

from pysqlite2 import dbapi2 as sqlite
import os, time

def predictions_distribution_total(cur, stats_dir):
  """Prints predictions distribution total (without AGCM Oracle)."""

  cur.execute("""SELECT COUNT(*)
                   FROM prediction
                  WHERE home != -1
                    AND away != -1
                    AND player_id != 44""")

  games_predicted = cur.fetchone()[0]

  cur.execute("""SELECT home, away, COUNT(*)
                   FROM prediction
                  WHERE home != -1
                    AND away != -1
                    AND player_id != 44
                  GROUP BY 1, 2
                  ORDER BY 3 DESC""")

  print 'Predictions:'
  i = 0
  f = open(os.path.join(stats_dir, "predictions_distribution.txt"), "w")
  for res in cur.fetchall():
    i += 1
    print "%2d. %2d - %2d %4d %6.2f%%" % (i, res[0], res[1], res[2], float(res[2]) / games_predicted * 100)
    f.write("%2d. %2d - %2d %4d %6.2f%%\n" % (i, res[0], res[1], res[2], float(res[2]) / games_predicted * 100))
  f.close()

def predictions_distribution_by_player(cur, player_stats_dir):
  """Prints predictions distribution by player."""

  cur.execute("""SELECT *
                   FROM player""")

  for player in cur.fetchall():
    cur.execute("""SELECT COUNT(*)
                     FROM prediction
                    WHERE home != -1
                      AND away != -1
                      AND player_id = ?""", (player[0], ))

    games_predicted = cur.fetchone()[0]

    cur.execute("""SELECT home, away, COUNT(*)
                     FROM prediction
                    WHERE home != -1
                      AND away != -1
                      AND player_id = ?
                    GROUP BY 1, 2
                    ORDER BY 3 DESC""", (player[0], ))
    
    i = 0
    f = open(os.path.join(player_stats_dir, 'predictions_distribution_%s.txt' % player[1].replace(' ', '_').replace('*', '_')), 'w')
    for res in cur.fetchall():
      i += 1
      f.write("%2d. %2d - %2d %4d %6.2f%%\n" % (i, res[0], res[1], res[2], float(res[2]) / games_predicted * 100))
    f.close()

def predictions_outcome_distribution_total(cur, stats_dir):
  """Prints predictions outcome distribution total."""

  hda = []

  cur.execute("""SELECT COUNT(*)
                   FROM prediction
                  WHERE home != -1
                    AND away != -1""")

  games_predicted = cur.fetchone()[0]

  cur.execute("""SELECT COUNT(*)
                   FROM prediction
                  WHERE home != -1
                    AND away != -1
                    AND home > away""")

  hda.append(cur.fetchone()[0])

  cur.execute("""SELECT COUNT(*)
                   FROM prediction
                  WHERE home != -1
                    AND away != -1
                    AND home = away""")

  hda.append(cur.fetchone()[0])
  hda.append(games_predicted - hda[0] - hda[1])

  print 'Home win / draw / away win (predictions):'
  f = open(os.path.join(stats_dir, "predictions_outcome_distribution.txt"), "w")
  for outcome in enumerate(['1', 'X', '2']):
    print "%s: %6d %6.2f%%" % (outcome[1], hda[outcome[0]], float(hda[outcome[0]]) / games_predicted * 100)
    f.write("%s: %6d %6.2f%%\n" % (outcome[1], hda[outcome[0]], float(hda[outcome[0]]) / games_predicted * 100))
  f.close()

def predictions_outcome_distribution_by_player(cur, player_stats_dir):
  """Prints predictions outcome distribution by player."""

  cur.execute("""SELECT *
                   FROM player""")

  for player in cur.fetchall():
    cur.execute("""SELECT COUNT(*)
                     FROM prediction
                    WHERE home != -1
                      AND away != -1
                      AND player_id = ?""", (player[0], ))

    games_predicted = cur.fetchone()[0]
    hda = []

    cur.execute("""SELECT COUNT(*)
                     FROM prediction
                    WHERE home != -1
                      AND away != -1
                      AND home > away
                      AND player_id = ?""", (player[0], ))
    hda.append(cur.fetchone()[0])

    cur.execute("""SELECT COUNT(*)
                     FROM prediction
                    WHERE home != -1
                      AND away != -1
                      AND home = away
                      AND player_id = ?""", (player[0], ))

    hda.append(cur.fetchone()[0])
    hda.append(games_predicted - hda[0] - hda[1])

    f = open(os.path.join(player_stats_dir, "predictions_outcome_distribution_%s.txt" % player[1].replace(' ', '_').replace('*', '_')), "w")
    for outcome in enumerate(['1', 'X', '2']):
      f.write("%s: %6d %6.2f%%\n" % (outcome[1], hda[outcome[0]], float(hda[outcome[0]]) / games_predicted * 100))
    f.close()

def results_distribution(cur, stats_dir):
  """Prints results distribution."""

  cur.execute("""SELECT COUNT(*)
                   FROM game
                  WHERE home_result != -1
                    AND away_result != -1""")

  games_played = cur.fetchone()[0]

  cur.execute("""SELECT home_result, away_result, COUNT(*)
                   FROM game
                  WHERE home_result != -1
                    AND away_result != -1
                  GROUP BY 1, 2
                  ORDER BY 3 DESC""")

  print 'Results:'
  i = 0
  f = open(os.path.join(stats_dir, "results_distribution.txt"), "w")
  for res in cur.fetchall():
    i += 1
    print "%2d. %2d - %2d %4d %6.2f%%" % (i, res[0], res[1], res[2], float(res[2]) / games_played * 100)
    f.write("%2d. %2d - %2d %4d %6.2f%%\n" % (i, res[0], res[1], res[2], float(res[2]) / games_played * 100))
  f.close()

def results_outcome_distribution(cur, stats_dir):
  """Prints results outcome distribution."""

  hda = []

  cur.execute("""SELECT COUNT(*)
                   FROM game
                  WHERE home_result != -1
                    AND away_result != -1""")

  games_played = cur.fetchone()[0]

  cur.execute("""SELECT COUNT(*)
                   FROM game
                  WHERE home_result != -1
                    AND away_result != -1
                    AND home_result > away_result""")

  hda.append(cur.fetchone()[0])

  cur.execute("""SELECT COUNT(*)
                   FROM game
                  WHERE home_result != -1
                    AND away_result != -1
                    AND home_result = away_result""")

  hda.append(cur.fetchone()[0])
  hda.append(games_played - hda[0] - hda[1])

  print 'Home win / draw / away win (results):'
  f = open(os.path.join(stats_dir, "results_outcome_distribution.txt"), "w")
  for outcome in enumerate(['1', 'X', '2']):
    print "%s: %6d %6.2f%%" % (outcome[1], hda[outcome[0]], float(hda[outcome[0]]) / games_played * 100)
    f.write("%s: %6d %6.2f%%\n" % (outcome[1], hda[outcome[0]], float(hda[outcome[0]]) / games_played * 100))
  f.close()

def player_predictions_made_total(cur, stats_dir):
  """Prints total predictions made."""

  cur.execute("""SELECT player.name, COUNT(*)
                   FROM prediction, player
                  WHERE prediction.player_id = player.id
                  GROUP BY player_id
                  ORDER BY 2 DESC, 1""")

  i = 0
  f = open(os.path.join(stats_dir, "number_of_predictions.txt"), "w")
  for res in cur.fetchall():
    i += 1
    f.write("%3d. %-35s %5d\n" % (i, res[0], res[1]))
  f.close()

def player_avg_pts_per_game(cur, stats_dir):
  """Prints players' average points per game."""

  cur.execute("""SELECT player.name, AVG(points), COUNT(*)
                   FROM prediction, player
                  WHERE prediction.player_id = player.id
                  GROUP BY player_id
                  ORDER BY 2 DESC, 1""")

  i = 0
  f = open(os.path.join(stats_dir, "average_points_scored.txt"), "w")
  for res in cur.fetchall():
    i += 1
    f.write("%3d. %-35s %5.3f %5d\n" % (i, res[0], res[1], res[2]))
  f.close()

def results_by_team(cur, team_stats_dir):
  """Prints results of all games by team."""

  cur.execute("""SELECT *
                   FROM team""")

  for team in cur.fetchall():
    cur.execute("""SELECT season.id, game.round_id, home.name, away.name, game.home_result, game.away_result
                     FROM season, game, team home, team away
                    WHERE (game.home_id = ? OR game.away_id = ?)
                      AND game.home_id = home.id
                      AND game.away_id = away.id
                      AND game.season_id = season.id
                      AND game.home_result != -1
                      AND game.away_result != -1
                    ORDER BY 1, 2""", (team[0], team[0]))

    i = 0
    f = open(os.path.join(team_stats_dir, 'results_%s.txt' % team[1].replace(' ', '_')), 'w')
    for res in cur.fetchall():
      i += 1
      f.write("%3d. %10s %2d %25s - %-25s %2d - %2d\n" % (i, res[0], res[1], res[2], res[3], res[4], res[5]))
    f.close()

def print_stats(filename, l):
  """Prints team stats to file."""

  f = open(filename, 'w')
  i = 0
  for res in l:
    i += 1
    f.write("%3d. %-22s %5.3f %4d\n" % (i, res[0], res[2], res[1]))
  f.close()

def query_team_stats(stats_dir, name_pattern, stat, min_games):
  """Retreives the team stats."""

  team_stats_query = """SELECT team.name, count, average
                          FROM team_stats, team
                         WHERE team_stats.stat_id = ?
                           AND team_stats.team_id = team.id
                           AND count >= ?
                         ORDER BY 3 %s, 2 DESC, 1"""

  filename = os.path.join(stats_dir, name_pattern % stat[1])
  sort_order = ('DESC' if stat[2] == 0 else 'ASC')
  cur.execute(team_stats_query % sort_order, (stat[0], min_games))
  l = cur.fetchall()
  print_stats(filename, l)

def team_stats(cur, stats_dir):
  """Prints all team stats described in team_stats_description table."""

  cur.execute("""SELECT id, title, sort_order
                   FROM team_stats_description
                  ORDER BY 1""")

  stats_list = cur.fetchall()

  for stat in stats_list:
    query_team_stats(stats_dir, '%s_all.txt', stat, 1)
    if stat[1].find('home') != -1 or stat[1].find('away') != -1:
      query_team_stats(stats_dir, '%s.txt', stat, 10)
    else:
      query_team_stats(stats_dir, '%s.txt', stat, 20)

def query_country_stats(country_stats_dir, name_pattern, stat, min_games):
  """Retreives the country stats."""

  country_stats_query = """SELECT country.name, count, average
                             FROM country_stats, country
                            WHERE country_stats.stat_id = ?
                              AND country_stats.country_id = country.id
                              AND count >= ?
                            ORDER BY 3 %s, 2 DESC, 1"""

  filename = os.path.join(country_stats_dir, name_pattern % stat[1])
  sort_order = ('DESC' if stat[2] == 0 else 'ASC')
  cur.execute(country_stats_query % sort_order, (stat[0], min_games))
  l = cur.fetchall()
  print_stats(filename, l)

def country_stats(cur, country_stats_dir):
  """Prints all country stats described in country_stats_description table."""

  cur.execute("""SELECT id, title, sort_order
                   FROM country_stats_description
                  ORDER BY 1""")

  stats_list = cur.fetchall()

  for stat in stats_list:
    query_country_stats(country_stats_dir, '%s.txt', stat, 1)

if __name__ == '__main__':
  stats_dir = 'stats'
  team_stats_dir = os.path.join(stats_dir, 'team')
  player_stats_dir = os.path.join(stats_dir, 'player')
  country_stats_dir = os.path.join(stats_dir, 'country')

  con = sqlite.connect('agcmpl.db')
  cur = con.cursor()
  time.clock()

  # print the stats
  predictions_distribution_total(cur, stats_dir)
  predictions_distribution_by_player(cur, player_stats_dir)
  predictions_outcome_distribution_total(cur, stats_dir)
  predictions_outcome_distribution_by_player(cur, player_stats_dir)
  results_distribution(cur, stats_dir)
  results_outcome_distribution(cur, stats_dir)
  player_predictions_made_total(cur, stats_dir)
  player_avg_pts_per_game(cur, stats_dir)
  results_by_team(cur, team_stats_dir)
  team_stats(cur, stats_dir)
  country_stats(cur, country_stats_dir)

  con.commit()
  print "Completed in %ss" % time.clock()

from pysqlite2 import dbapi2 as sqlite
import os

stats_dir = 'stats'
team_stats_dir = os.path.join(stats_dir, 'team')
player_stats_dir = os.path.join(stats_dir, 'player')

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

# predictions distribution by player

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
  
  #print 'Predictions for %s:' % player[1]
  j = 0
  f = open(os.path.join(player_stats_dir, 'predictions_distribution_%s.txt' % player[1].replace(' ', '_').replace('*', '_')), 'w')
  for res in cur.fetchall():
    j += 1
    #print "%2d. %2d - %2d %4d %6.2f%%" % (j, res[0], res[1], res[2], float(res[2]) / games_predicted * 100)
    f.write("%2d. %2d - %2d %4d %6.2f%%\n" % (j, res[0], res[1], res[2], float(res[2]) / games_predicted * 100))
  f.close()

# predictions distribution total (without AGCM Oracle)

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

# results distribution

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

# results - outcome distribution

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

# predictions - outcome distribution total

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

# predictions - outcome distribution by player

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

# results of all games by team

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

  j = 0
  f = open(os.path.join(team_stats_dir, 'results_%s.txt' % team[1].replace(' ', '_')), 'w')
  for res in cur.fetchall():
    j += 1
    f.write("%3d. %10s %2d %25s - %-25s %2d - %2d\n" % (j, res[0], res[1], res[2], res[3], res[4], res[5]))
  f.close()
  #print 'Done: %s' % team[1]

con.commit()

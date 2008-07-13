from pysqlite2 import dbapi2 as sqlite
from pl_constants import *
import os, time

def get_seasons():
  """Returns a list of season ids."""

  cur.execute("SELECT id FROM season")
  return [t[0] for t in cur.fetchall()]

def predictions_distribution_total():
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
    print "%2d. %2d - %2d %6d %6.2f%%" % (i, res[0], res[1], res[2], float(res[2]) / games_predicted * 100)
    f.write("%2d. %2d - %2d %6d %6.2f%%\n" % (i, res[0], res[1], res[2], float(res[2]) / games_predicted * 100))
  f.close()

def predictions_distribution_by_player():
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

def predictions_outcome_distribution_total():
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

def predictions_outcome_distribution_by_player():
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

def results_distribution():
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

def results_outcome_distribution():
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

def player_predictions_made_total():
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

def player_avg_pts_per_game():
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

def results_by_team():
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

def stats_by_team():
  """Prints all team stats described in team_stats_description by team."""

  cur.execute("""SELECT *
                   FROM team""")

  for team in cur.fetchall():
    cur.execute("""SELECT description, average
                     FROM team, team_stats, team_stats_description
                    WHERE team.id = ?
                      AND team_stats.team_id = team.id
                      AND team_stats.stat_id = team_stats_description.id
                      AND team_stats.season_id = ?
                    ORDER BY team_stats.stat_id""", (team[0], all_seasons_const))

    f = open(os.path.join(team_stats_dir, 'stats_%s.txt' % team[1].replace(' ', '_')), 'w')
    for res in cur.fetchall():
      f.write("%-35s = %5.3f\n" % tuple(res))
    f.close()

def print_stats(filename, l):
  """Prints team stats to file."""

  f = open(filename, 'w')
  i = 0
  for res in l:
    i += 1
    f.write("%3d. %-22s %5.3f %4d\n" % (i, res[0], res[2], res[1]))
  f.close()

def query_team_stats(name_pattern, season, stat, min_games):
  """Retreives the team stats."""

  team_stats_query = """SELECT team.name, count, average
                          FROM team_stats, team
                         WHERE team_stats.stat_id = ?
                           AND team_stats.team_id = team.id
                           AND season_id = ?
                           AND count >= ?
                         ORDER BY 3 %s, 2 DESC, 1"""

  if season != all_seasons_const:
    filename = os.path.join(seasons_dir, season, name_pattern % stat[1])
  else:
    filename = os.path.join(stats_dir, name_pattern % stat[1])
  sort_order = ('DESC' if stat[2] == 0 else 'ASC')
  cur.execute(team_stats_query % sort_order, (stat[0], season, min_games))
  l = cur.fetchall()
  print_stats(filename, l)

def team_stats():
  """Prints all team stats described in team_stats_description table."""

  cur.execute("""SELECT id, title, sort_order
                   FROM team_stats_description
                  ORDER BY 1""")

  stats_list = cur.fetchall()
  seasons = get_seasons()
  seasons.append(all_seasons_const)

  for season in seasons:
    s_dir = os.path.join(seasons_dir, season)
    if not os.path.exists(s_dir) and season != all_seasons_const:
      os.makedirs(s_dir)
    for stat in stats_list:
      query_team_stats('%s_all.txt', season, stat, 1)
      if season == all_seasons_const:
        if stat[1].find('home') != -1 or stat[1].find('away') != -1:
          query_team_stats('%s.txt', season, stat, 10)
        else:
          query_team_stats('%s.txt', season, stat, 20)

def query_country_stats(name_pattern, season, stat, min_games):
  """Retreives the country stats."""

  country_stats_query = """SELECT country.name, count, average
                             FROM country_stats, country
                            WHERE country_stats.stat_id = ?
                              AND country_stats.country_id = country.id
                              AND season_id = ?
                              AND count >= ?
                            ORDER BY 3 %s, 2 DESC, 1"""

  if season != all_seasons_const:
    filename = os.path.join(country_seasons_dir, season, name_pattern % stat[1])
  else:
    filename = os.path.join(country_stats_dir, name_pattern % stat[1])
  sort_order = ('DESC' if stat[2] == 0 else 'ASC')
  cur.execute(country_stats_query % sort_order, (stat[0], season, min_games))
  l = cur.fetchall()
  print_stats(filename, l)

def country_stats():
  """Prints all country stats described in country_stats_description table."""

  cur.execute("""SELECT id, title, sort_order
                   FROM country_stats_description
                  ORDER BY 1""")

  stats_list = cur.fetchall()
  seasons = get_seasons()
  seasons.append(all_seasons_const)

  for season in seasons:
    s_dir = os.path.join(country_seasons_dir, season)
    if not os.path.exists(s_dir) and season != all_seasons_const:
      os.makedirs(s_dir)
    for stat in stats_list:
      query_country_stats('%s.txt', season, stat, 1)

def most_predictable_games(count):
  """Prints top (count) most predictable games."""

  cur.execute("""SELECT game.season_id, game.round_id, t1.name, t2.name, game.home_result, game.away_result, sum, average
                   FROM game_predictability, game, team t1, team t2
                  WHERE game_predictability.game_id = game.id
                    AND game.home_id = t1.id
                    AND game.away_id = t2.id
                  ORDER BY 8 DESC, 7 DESC""")

  print "Most predictable games:"
  i = 0
  f = open(os.path.join(stats_dir, "most_predictable_games.txt"), "w")
  for res in cur.fetchall()[:count]:
    i += 1
    l = [i]
    for val in res:
      l.append(val)
    print "%2d. [%7s, %2d] %22s - %-22s %2d - %2d  %3d  %5.3f" % tuple(l)
    f.write("%2d. [%7s, %2d] %22s - %-22s %2d - %2d  %3d  %5.3f\n" % tuple(l))
  f.close()

def team_rating():
  """Prints most overrated teams, per season and overall."""

  query = """SELECT team.name, t1.average - t2.average, t1.count
               FROM team, team_stats t1, team_stats t2, team_stats_description t1d, team_stats_description t2d
              WHERE team.id = t1.team_id
                AND t1.team_id = t2.team_id
                AND t1.stat_id = t1d.id
                AND t2.stat_id = t2d.id
                AND t1.season_id = ?
                AND t2.season_id = ?
                AND t1d.title = ?
                AND t2d.title = ?
              ORDER BY 2 DESC, 3 DESC"""

  seasons = get_seasons()
  seasons.append(all_seasons_const)

  for season in seasons:
    for stat in ['', '_home', '_away']:
      cur.execute(query, (season, season, 'predicted_team_success%s' % stat, 'team_success%s' % stat))
      res = cur.fetchall()
      i, j = 0, 0
      if season != all_seasons_const:
        f_all = open(os.path.join(seasons_dir, season, "most_overrated_teams_diff%s_all.txt" % stat), "w")
      else:
        f_all = open(os.path.join(stats_dir, "most_overrated_teams_diff%s_all.txt" % stat), "w")
        f = open(os.path.join(stats_dir, "most_overrated_teams_diff%s.txt" % stat), "w")
      for team in res:
        i += 1
        f_all.write("%3d. %-22s %+5.3f %4d\n" % (i, team[0], team[1], team[2]))
        if season == all_seasons_const and ((team[2] >= 20 and stat == '') or (team[2] >= 10 and stat != '')):
          j += 1
          f.write("%3d. %-22s %+5.3f %4d\n" % (j, team[0], team[1], team[2]))
      if season == all_seasons_const:
        f.close()
      f_all.close()

def country_rating():
  """Prints most overrated countries, per season and overall."""

  query = """SELECT country.name, c1.average - c2.average, c1.count
               FROM country, country_stats c1, country_stats c2, country_stats_description c1d, country_stats_description c2d
              WHERE country.id = c1.country_id
                AND c1.country_id = c2.country_id
                AND c1.stat_id = c1d.id
                AND c2.stat_id = c2d.id
                AND c1.season_id = ?
                AND c2.season_id = ?
                AND c1d.title = ?
                AND c2d.title = ?
              ORDER BY 2 DESC, 3 DESC"""

  seasons = get_seasons()
  seasons.append(all_seasons_const)

  for season in seasons:
    for stat in ['', '_home', '_away']:
      cur.execute(query, (season, season, 'predicted_country_success%s' % stat, 'country_success%s' % stat))
      res = cur.fetchall()
      i = 0
      if season != all_seasons_const:
        f_all = open(os.path.join(country_seasons_dir, season, "most_overrated_countries_diff%s_all.txt" % stat), "w")
      else:
        f_all = open(os.path.join(country_stats_dir, "most_overrated_countries_diff%s_all.txt" % stat), "w")
      for country in res:
        i += 1
        f_all.write("%3d. %-22s %+5.3f %4d\n" % (i, country[0], country[1], country[2]))
      f_all.close()


stats_dir = 'stats'
team_stats_dir = os.path.join(stats_dir, 'team')
player_stats_dir = os.path.join(stats_dir, 'player')
seasons_dir = os.path.join(stats_dir, 'season')
country_stats_dir = os.path.join(stats_dir, 'country')
country_seasons_dir = os.path.join(country_stats_dir, 'season')

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

if __name__ == '__main__':
  time.clock()

  # print the overall stats
  predictions_distribution_total()
  predictions_distribution_by_player()
  predictions_outcome_distribution_total()
  predictions_outcome_distribution_by_player()
  results_distribution()
  results_outcome_distribution()
  player_predictions_made_total()
  player_avg_pts_per_game()
  results_by_team()
  stats_by_team()
  team_stats()
  country_stats()
  most_predictable_games(20)
  team_rating()
  country_rating()

  print "Completed in %ss" % time.clock()

con.commit()

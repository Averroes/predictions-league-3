from pysqlite2 import dbapi2 as sqlite
from pl_constants import *
import os, time

# helper functions

def prepare_data(index, row_data, avg_index = -1, count = -1):
  """Prefixes a row returned by an SQL query with an index and calculates the
     average of a column if needed."""

  if avg_index == -1:
    return tuple([index] + list(row_data))
  else:
    return tuple([index] + list(row_data) + [float(row_data[avg_index]) / count * 100])

def get_seasons():
  """Returns a list of season ids."""

  cur.execute("SELECT id FROM season")
  return [t[0] for t in cur.fetchall()]

def get_games_played(season = all_seasons_const):
  """Returns number of games played in a given season. If called with no argument
     or with all_seasons_const as the season argument, returns total games played
     in all seasons."""
  
  games_played_query = """SELECT COUNT(*)
                            FROM game
                           WHERE home_result != -1
                             AND away_result != -1
                             %s"""

  season_query = "AND season_id = ?"

  if season != all_seasons_const:
    cur.execute(games_played_query % season_query, (season, ))
  else:
    cur.execute(games_played_query % '')
  
  return cur.fetchone()[0]

def get_games_predicted_and_outcome_count(player = None, season = all_seasons_const):
  """Returns number of predicted games by a player in a given season and a list of
     prediction outcome counts."""

  games_predicted_query = """SELECT COUNT(*),
                                    SUM(CASE WHEN home > away THEN 1 ELSE 0 END),
                                    SUM(CASE WHEN home = away THEN 1 ELSE 0 END),
                                    SUM(CASE WHEN home < away THEN 1 ELSE 0 END)
                               FROM prediction
                              WHERE home != -1
                                AND away != -1
                                 %s"""

  games_predicted_season_query = """SELECT COUNT(*),
                                           SUM(CASE WHEN home > away THEN 1 ELSE 0 END),
                                           SUM(CASE WHEN home = away THEN 1 ELSE 0 END),
                                           SUM(CASE WHEN home < away THEN 1 ELSE 0 END)
                                      FROM prediction, game
                                     WHERE prediction.game_id = game.id
                                       AND home != -1
                                       AND away != -1
                                       %s
                                       %s"""

  player_query = "AND player_id = ?"
  season_query = "AND season_id = ?"

  if player != None: # single player
    if season != all_seasons_const: # single season
       cur.execute(games_predicted_season_query % (player_query, season_query), (player, season))
    else: # all seasons
       cur.execute(games_predicted_query % player_query, (player, ))
  else: # all players
    if season != all_seasons_const: # single season
       cur.execute(games_predicted_season_query % ('', season_query), (season, ))
    else: # all seasons
       cur.execute(games_predicted_query % '')

  count = cur.fetchone()
  return count[0], count[1:]

def get_prediction_distribution(season = all_seasons_const):
  """Returns number of predicted games by a player in a given season and a list of
     prediction outcome counts."""

  predictions_distribution_query = """SELECT home, away, COUNT(*)
                                        FROM prediction, game
                                       WHERE prediction.game_id = game.id
                                         AND home != -1
                                         AND away != -1
                                         %s
                                       GROUP BY 1, 2
                                       ORDER BY 3 DESC"""

  season_query = "AND season_id = ?"

  if season != all_seasons_const:
     cur.execute(predictions_distribution_query % season_query, (season, ))
  else:
     cur.execute(predictions_distribution_query % '')

  return cur.fetchall()

def get_result_outcome_count(outcome, season = all_seasons_const):
  """Returns a number of games (from a given season) that finished in a given outcome."""

  outcome_count_query = """SELECT COUNT(*)
                             FROM game
                            WHERE home_result != -1
                              AND away_result != -1
                              AND home_result %s away_result
                              %s"""

  season_query = "AND season_id = ?"
  
  if outcome == home_win_const:
    operator = '>'
  elif outcome == draw_const:
    operator = '='
  elif outcome == away_win_const:
    operator = '<'
  else:
    return -1

  if season != all_seasons_const:
    cur.execute(outcome_count_query % (operator, season_query), (season, ))
  else:
    cur.execute(outcome_count_query % (operator, ''))

  return cur.fetchone()[0]

def get_player_id(name):
  """Returns id of player with given name."""
  
  cur.execute("""SELECT id
                   FROM player
                  WHERE name = ?""", (name, ))

  return cur.fetchone()[0]

# stats functions

def predictions_distribution_total():
  """Prints predictions distribution total (without AGCM Oracle)."""

  oracle_id = get_player_id('AGCM Oracle')

  games_predicted_query = """SELECT COUNT(*)
                               FROM prediction
                              WHERE home != -1
                                AND away != -1
                                AND player_id != ?"""

  games_predicted_season_query = """SELECT COUNT(*)
                                      FROM prediction, game
                                     WHERE prediction.game_id = game.id
                                       AND home != -1
                                       AND away != -1
                                       AND player_id != ?
                                       AND season_id = ?"""

  seasons = get_seasons()
  seasons.append(all_seasons_const)

  for season in seasons:
    if season != all_seasons_const:
      cur.execute(games_predicted_season_query, (oracle_id, season))
      games_predicted = cur.fetchone()[0]
      distribution = get_prediction_distribution(season)
      s_dir = os.path.join(seasons_dir, season)
      if not os.path.exists(s_dir):
        os.makedirs(s_dir)
      f = open(os.path.join(s_dir, "predictions_distribution.txt"), "w")
    else:
      cur.execute(games_predicted_query, (oracle_id, ))
      games_predicted = cur.fetchone()[0]
      distribution = get_prediction_distribution()
      print 'Predictions:'
      f = open(os.path.join(stats_dir, "predictions_distribution.txt"), "w")

    i = 0
    for res in distribution:
      i += 1
      f.write("%2d. %2d - %2d %6d %6.2f%%\n" % prepare_data(i, res, len(res) - 1, games_predicted))
      if season == all_seasons_const:
        print "%2d. %2d - %2d %6d %6.2f%%" % prepare_data(i, res, len(res) - 1, games_predicted)
    f.close()

def predictions_distribution_by_player():
  """Prints predictions distribution by player."""

  cur.execute("""SELECT *
                   FROM player""")

  for player in cur.fetchall():
    games_predicted, hda = get_games_predicted_and_outcome_count(player[0])

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
      f.write("%2d. %2d - %2d %6d %6.2f%%\n" % prepare_data(i, res, len(res) - 1, games_predicted))
    f.close()

def predictions_outcome_distribution_total():
  """Prints predictions outcome distribution total."""

  seasons = get_seasons()
  seasons.append(all_seasons_const)

  for season in seasons:
    games_predicted, hda = get_games_predicted_and_outcome_count(season = season)

    if season != all_seasons_const:
      f = open(os.path.join(seasons_dir, season, "predictions_outcome_distribution.txt"), "w")
    else:
      print 'Home win / draw / away win (predictions):'
      f = open(os.path.join(stats_dir, "predictions_outcome_distribution.txt"), "w")
    for outcome in enumerate([home_win_const, draw_const, away_win_const]):
      f.write("%s: %6d %6.2f%%\n" % (outcome[1], hda[outcome[0]], float(hda[outcome[0]]) / games_predicted * 100))
      if season == all_seasons_const:
        print "%s: %6d %6.2f%%" % (outcome[1], hda[outcome[0]], float(hda[outcome[0]]) / games_predicted * 100)
    f.close()

def predictions_outcome_distribution_by_player():
  """Prints predictions outcome distribution by player."""

  cur.execute("""SELECT *
                   FROM player""")

  for player in cur.fetchall():
    games_predicted, hda = get_games_predicted_and_outcome_count(player[0])

    f = open(os.path.join(player_stats_dir, "predictions_outcome_distribution_%s.txt" % player[1].replace(' ', '_').replace('*', '_')), "w")
    for outcome in enumerate([home_win_const, draw_const, away_win_const]):
      f.write("%s: %6d %6.2f%%\n" % (outcome[1], hda[outcome[0]], float(hda[outcome[0]]) / games_predicted * 100))
    f.close()

def results_distribution():
  """Prints results distribution."""

  results_query = """SELECT home_result, away_result, COUNT(*)
                       FROM game
                      WHERE home_result != -1
                        AND away_result != -1
                        %s
                      GROUP BY 1, 2
                      ORDER BY 3 DESC"""

  season_query = "AND SEASON_ID = ?"

  seasons = get_seasons()
  seasons.append(all_seasons_const)

  for season in seasons:
    games_played = get_games_played(season)
    if season != all_seasons_const:
      cur.execute(results_query % season_query, (season, ))
      filename = os.path.join(seasons_dir, season, "results_distribution.txt")
    else:
      cur.execute(results_query % '')
      filename = os.path.join(stats_dir, "results_distribution.txt")
      print 'Results:'
    f = open(filename, 'w')
    i = 0
    for res in cur.fetchall():
      i += 1
      f.write("%2d. %2d - %2d %4d %6.2f%%\n" % prepare_data(i, res, len(res) - 1, games_played))
      if season == all_seasons_const:
        print "%2d. %2d - %2d %4d %6.2f%%" % prepare_data(i, res, len(res) - 1, games_played)
    f.close()

def results_outcome_distribution():
  """Prints results outcome distribution."""

  seasons = get_seasons()
  seasons.append(all_seasons_const)

  for season in seasons:
    hda = []
    hda.append(get_result_outcome_count(home_win_const, season))
    hda.append(get_result_outcome_count(draw_const, season))
    hda.append(get_result_outcome_count(away_win_const, season))
    games_played = get_games_played(season)

    if season != all_seasons_const:
      f = open(os.path.join(seasons_dir, season, "results_outcome_distribution.txt"), "w")
    else:
      print 'Home win / draw / away win (results):'
      f = open(os.path.join(stats_dir, "results_outcome_distribution.txt"), "w")
    for outcome in enumerate([home_win_const, draw_const, away_win_const]):
      f.write("%s: %6d %6.2f%%\n" % (outcome[1], hda[outcome[0]], float(hda[outcome[0]]) / games_played * 100))
      if season == all_seasons_const:
        print "%s: %6d %6.2f%%" % (outcome[1], hda[outcome[0]], float(hda[outcome[0]]) / games_played * 100)
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
    f.write("%3d. %-35s %5d\n" % prepare_data(i, res))
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
    f.write("%3d. %-35s %5.3f %5d\n" % prepare_data(i, res))
  f.close()

def results_by_team():
  """Prints results of all games by team."""

  cur.execute("""SELECT *
                   FROM team""")

  for team in cur.fetchall():
    cur.execute("""SELECT season.id, game.round_id, home.name, away.name, game.home_result, game.away_result,
                          CASE WHEN game.home_id = ? THEN game.home_points ELSE game.away_points END
                     FROM season, game, team home, team away
                    WHERE (game.home_id = ? OR game.away_id = ?)
                      AND game.home_id = home.id
                      AND game.away_id = away.id
                      AND game.season_id = season.id
                      AND game.home_result != -1
                      AND game.away_result != -1
                    ORDER BY 1, 2""", (team[0], team[0], team[0]))

    i = 0
    f = open(os.path.join(team_stats_dir, 'results_%s.txt' % team[1].replace(' ', '_')), 'w')
    for res in cur.fetchall():
      i += 1
      f.write("%3d. %10s %2d %25s - %-25s %2d - %2d  %d\n" % prepare_data(i, res))
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
      f.write("%-35s = %5.3f\n" % res)
    f.close()

def print_stats(filename, l, name_len=22):
  """Prints team or country stats to file."""

  format_str = "".join(["%3d. %-", str(name_len), "s %5.3f %4d\n"])

  f = open(filename, 'w')
  i = 0
  for res in l:
    i += 1
    f.write(format_str % prepare_data(i, res))
  f.close()

def query_team_stats(name_pattern, season, stat, min_games):
  """Retreives the team stats."""

  team_stats_query = """SELECT team.name, average, count
                          FROM team_stats, team
                         WHERE team_stats.stat_id = ?
                           AND team_stats.team_id = team.id
                           AND season_id = ?
                           AND count >= ?
                         ORDER BY 2 %s, 3 DESC, 1"""

  if season != all_seasons_const:
    filename = os.path.join(seasons_dir, season, name_pattern % stat[1])
  else:
    filename = os.path.join(stats_dir, name_pattern % stat[1])
  sort_order = ('DESC' if stat[2] == sort_desc else 'ASC')
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

  country_stats_query = """SELECT country.name, average, count
                             FROM country_stats, country
                            WHERE country_stats.stat_id = ?
                              AND country_stats.country_id = country.id
                              AND season_id = ?
                              AND count >= ?
                            ORDER BY 2 %s, 3 DESC, 1"""

  if season != all_seasons_const:
    filename = os.path.join(country_seasons_dir, season, name_pattern % stat[1])
  else:
    filename = os.path.join(country_stats_dir, name_pattern % stat[1])
  sort_order = ('DESC' if stat[2] == sort_desc else 'ASC')
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
    print "%2d. [%7s, %2d] %22s - %-22s %2d - %2d  %3d  %5.3f" % prepare_data(i, res)
    f.write("%2d. [%7s, %2d] %22s - %-22s %2d - %2d  %3d  %5.3f\n" % prepare_data(i, res))
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

def query_player_team_stats_by_team(name_pattern, season, stat, min_games):
  """Retreives the player_team stats by team."""

  cur.execute("""SELECT *
                   FROM team""")
  team_list = cur.fetchall()
  
  player_team_stats_query = """SELECT player.name, average, count
                                 FROM player_team_stats, player
                                WHERE player_team_stats.player_id = player.id
                                  AND player_team_stats.stat_id = ?
                                  AND player_team_stats.team_id = ?
                                  AND season_id = ?
                                  AND count >= ?
                                ORDER BY 2 %s, 3 DESC, 1"""

  sort_order = ('DESC' if stat[2] == sort_desc else 'ASC')
  for team in team_list:
    if season != all_seasons_const:
      filename = os.path.join(team_seasons_dir, season, name_pattern % (stat[1], team[1].replace(' ', '_')))
    else:
      filename = os.path.join(team_stats_dir, name_pattern % (stat[1], team[1].replace(' ', '_')))
    cur.execute(player_team_stats_query % sort_order, (stat[0], team[0], season, min_games))
    l = cur.fetchall()
    if l:
      print_stats(filename, l, 30)

def query_player_team_stats_by_player(name_pattern, season, stat, min_games):
  """Retreives the player_team stats by player."""

  cur.execute("""SELECT *
                   FROM player""")
  player_list = cur.fetchall()
  
  player_team_stats_query = """SELECT team.name, average, count
                                 FROM player_team_stats, team
                                WHERE player_team_stats.team_id = team.id
                                  AND player_team_stats.stat_id = ?
                                  AND player_team_stats.player_id = ?
                                  AND season_id = ?
                                  AND count >= ?
                                ORDER BY 2 %s, 3 DESC, 1"""

  sort_order = ('DESC' if stat[2] == sort_desc else 'ASC')
  for player in player_list:
    if season != all_seasons_const:
      filename = os.path.join(player_seasons_dir, season, name_pattern % (stat[1], player[1].replace(' ', '_').replace('*', '_')))
    else:
      filename = os.path.join(player_stats_dir, name_pattern % (stat[1], player[1].replace(' ', '_').replace('*', '_')))
    cur.execute(player_team_stats_query % sort_order, (stat[0], player[0], season, min_games))
    l = cur.fetchall()
    if l:
      print_stats(filename, l)

def player_team_stats():
  """Prints all player_team stats described in player_team_stats_description table."""

  cur.execute("""SELECT id, title, sort_order
                   FROM player_team_stats_description
                  ORDER BY 1""")

  stats_list = cur.fetchall()
  seasons = get_seasons()
  seasons.append(all_seasons_const)

  for season in seasons:
    s_dir = os.path.join(team_seasons_dir, season)
    p_dir = os.path.join(player_seasons_dir, season)
    if not os.path.exists(s_dir) and season != all_seasons_const:
      os.makedirs(s_dir)
    if not os.path.exists(p_dir) and season != all_seasons_const:
      os.makedirs(p_dir)
    for stat in stats_list:
      if season == all_seasons_const:
        query_player_team_stats_by_team('%s_%s_all.txt', season, stat, 1)
        query_player_team_stats_by_player('%s_%s_all.txt', season, stat, 1)
        query_player_team_stats_by_team('%s_%s.txt', season, stat, 10)
        query_player_team_stats_by_player('%s_%s.txt', season, stat, 10)
      else:
        query_player_team_stats_by_team('%s_%s.txt', season, stat, 1)
        query_player_team_stats_by_player('%s_%s.txt', season, stat, 1)

stats_dir = 'stats'
team_stats_dir = os.path.join(stats_dir, 'team')
team_seasons_dir = os.path.join(team_stats_dir, 'season')
player_stats_dir = os.path.join(stats_dir, 'player')
player_seasons_dir = os.path.join(player_stats_dir, 'season')
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
  player_team_stats()

  print "Completed in %ss" % time.clock()

con.commit()

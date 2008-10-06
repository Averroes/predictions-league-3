from pysqlite2 import dbapi2 as sqlite
from pl_constants import *
import time

def get_seasons():
  """Returns a list of season ids."""

  cur.execute("SELECT id FROM season")
  return [t[0] for t in cur.fetchall()]

def calculate_stats(stat_sql, stat_id, key, stat, season):
  """Executes the insert statement for a given stat and season."""

  cur.execute(stat_sql % (stat_id, key, stat, stat), (season, ))

def get_season_total(home_stat_id, away_stat_id, total_stat_id, season):
  """Calculates overall stats for given season (home and away combined)."""

  total_insert = """INSERT INTO player_team_stats
                         SELECT %s, player_id, team_id, season_id, SUM(sum), SUM(count), CAST(SUM(sum) AS FLOAT) / SUM(count)
                           FROM player_team_stats
                          WHERE (stat_id = %s OR stat_id = %s)
                            AND season_id = ?
                          GROUP BY player_id, team_id"""

  cur.execute(total_insert % (total_stat_id, home_stat_id, away_stat_id), (season, ))

def sum_all_seasons(all_seasons_const):
  """Calculates overall stats for all seasons (home and away combined)."""

  total_insert = """INSERT INTO player_team_stats
                         SELECT stat_id, player_id, team_id, '%s', SUM(sum), SUM(count), CAST(SUM(sum) AS FLOAT) / SUM(count)
                           FROM player_team_stats
                          GROUP BY stat_id, player_id, team_id"""

  cur.execute(total_insert % all_seasons_const)


con = sqlite.connect('agcmpl.db')
cur = con.cursor()
time.clock()

stat_insert = """INSERT INTO player_team_stats
                      SELECT %s, player_id, game.%s, season_id, SUM(%s), COUNT(*), CAST(SUM(%s) AS FLOAT) / COUNT(*)
                        FROM prediction, game
                       WHERE prediction.game_id = game.id
                         AND season_id = ?
                       GROUP BY 2, 3, 4
                       ORDER BY 2, 3, 4"""

# calculate stats and insert into player_team_stats

cur.execute('DELETE FROM player_team_stats')

seasons = get_seasons()
for season in seasons:
  calculate_stats(stat_insert, prediction_success_home_stat_id, 'home_id', 'points', season) # prediction success home
  calculate_stats(stat_insert, prediction_success_away_stat_id, 'away_id', 'points', season) # prediction success away
  get_season_total(prediction_success_home_stat_id, prediction_success_away_stat_id, prediction_success_total_stat_id, season)

  print 'Season %s stats done.' % season

sum_all_seasons(all_seasons_const)

# insert stat descriptions into player_team_stats_description

description_insert = """INSERT INTO player_team_stats_description
                             VALUES(?, ?, ?, ?)"""

cur.execute('DELETE FROM player_team_stats_description')
cur.execute(description_insert, (prediction_success_home_stat_id, 'prediction_success_home', sort_desc, 'Avg. prediction points scored home'))
cur.execute(description_insert, (prediction_success_away_stat_id, 'prediction_success_away', sort_desc, 'Avg. prediction points scored away'))
cur.execute(description_insert, (prediction_success_total_stat_id, 'prediction_success', sort_desc, 'Avg. prediction points scored'))

con.commit()
print "Completed in %ss" % time.clock()

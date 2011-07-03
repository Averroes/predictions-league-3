from sqlite3 import dbapi2 as sqlite
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

  total_insert = """INSERT INTO team_stats(stat_id, team_id, season_id, sum, count, average)
                         SELECT %s, team_id, season_id, SUM(sum), SUM(count), CAST(SUM(sum) AS FLOAT) / SUM(count)
                           FROM team_stats
                          WHERE (stat_id = %s OR stat_id = %s)
                            AND season_id = ?
                          GROUP BY team_id"""

  cur.execute(total_insert % (total_stat_id, home_stat_id, away_stat_id), (season, ))

def sum_all_seasons(all_seasons_const):
  """Calculates overall stats for all seasons (home and away combined)."""

  total_insert = """INSERT INTO team_stats(stat_id, team_id, season_id, sum, count, average)
                         SELECT stat_id, team_id, '%s', SUM(sum), SUM(count), CAST(SUM(sum) AS FLOAT) / SUM(count)
                           FROM team_stats
                          GROUP BY stat_id, team_id"""

  cur.execute(total_insert % all_seasons_const)


con = sqlite.connect('agcmpl.db')
cur = con.cursor()
time.clock()

stat_insert = """INSERT INTO team_stats(stat_id, team_id, season_id, sum, count, average)
                      SELECT %s, %s, season_id, SUM(%s), COUNT(*), CAST(SUM(%s) AS FLOAT) / COUNT(*)
                        FROM game
                       WHERE season_id = ?
                       GROUP BY 2, 3
                       ORDER BY 2, 3"""

prediction_success_insert = """INSERT INTO team_stats(stat_id, team_id, season_id, sum, count, average)
                                    SELECT %s, %s, season_id, SUM(%s), COUNT(*), CAST(SUM(%s) AS FLOAT) / COUNT(*)
                                      FROM game_predictability
                                     WHERE season_id = ?
                                     GROUP BY 2, 3
                                     ORDER BY 2, 3"""

# calculate stats and insert into team_stats

cur.execute('DELETE FROM team_stats')
seasons = get_seasons()
for season in seasons:
  calculate_stats(stat_insert, goals_scored_home_stat_id, 'home_id', 'home_result', season) # goals scored home
  calculate_stats(stat_insert, goals_scored_away_stat_id, 'away_id', 'away_result', season) # goals scored away
  get_season_total(goals_scored_home_stat_id, goals_scored_away_stat_id, goals_scored_total_stat_id, season)

  calculate_stats(stat_insert, goals_conceded_home_stat_id, 'home_id', 'away_result', season) # goals conceded home
  calculate_stats(stat_insert, goals_conceded_away_stat_id, 'away_id', 'home_result', season) # goals conceded away
  get_season_total(goals_conceded_home_stat_id, goals_conceded_away_stat_id, goals_conceded_total_stat_id, season)

  calculate_stats(stat_insert, success_home_stat_id, 'home_id', 'home_points', season) # team success home
  calculate_stats(stat_insert, success_away_stat_id, 'away_id', 'away_points', season) # team success away
  get_season_total(success_home_stat_id, success_away_stat_id, success_total_stat_id, season)

  calculate_stats(prediction_success_insert, predicted_success_home_stat_id, 'home_id', 'home_points', season) # predicted home success
  calculate_stats(prediction_success_insert, predicted_success_away_stat_id, 'away_id', 'away_points', season) # predicted away success
  get_season_total(predicted_success_home_stat_id, predicted_success_away_stat_id, predicted_success_total_stat_id, season)

  calculate_stats(prediction_success_insert, prediction_success_home_stat_id, 'home_id', 'average', season) # prediction success home
  calculate_stats(prediction_success_insert, prediction_success_away_stat_id, 'away_id', 'average', season) # prediction success away
  get_season_total(prediction_success_home_stat_id, prediction_success_away_stat_id, prediction_success_total_stat_id, season)

  print 'Season %s stats done.' % season

sum_all_seasons(all_seasons_const)

# insert stat descriptions into team_stats_description

description_insert = """INSERT INTO team_stats_description
                             VALUES(?, ?, ?, ?)"""

cur.execute('DELETE FROM team_stats_description')
cur.execute(description_insert, (goals_scored_home_stat_id, 'goals_scored_home', sort_desc, 'Avg. goals scored home'))
cur.execute(description_insert, (goals_scored_away_stat_id, 'goals_scored_away', sort_desc, 'Avg. goals scored away'))
cur.execute(description_insert, (goals_scored_total_stat_id, 'goals_scored', sort_desc, 'Avg. goals scored'))
cur.execute(description_insert, (goals_conceded_home_stat_id, 'goals_conceded_home', sort_asc, 'Avg. goals conceded home'))
cur.execute(description_insert, (goals_conceded_away_stat_id, 'goals_conceded_away', sort_asc, 'Avg. goals conceded away'))
cur.execute(description_insert, (goals_conceded_total_stat_id, 'goals_conceded', sort_asc, 'Avg. goals conceded'))
cur.execute(description_insert, (success_home_stat_id, 'team_success_home', sort_desc, 'Avg. points scored home'))
cur.execute(description_insert, (success_away_stat_id, 'team_success_away', sort_desc, 'Avg. points scored away'))
cur.execute(description_insert, (success_total_stat_id, 'team_success', sort_desc, 'Avg. points scored'))
cur.execute(description_insert, (predicted_success_home_stat_id, 'predicted_team_success_home', sort_desc, 'Avg. points predicted home'))
cur.execute(description_insert, (predicted_success_away_stat_id, 'predicted_team_success_away', sort_desc, 'Avg. points predicted away'))
cur.execute(description_insert, (predicted_success_total_stat_id, 'predicted_team_success', sort_desc, 'Avg. points predicted'))
cur.execute(description_insert, (prediction_success_home_stat_id, 'prediction_success_home', sort_desc, 'Avg. prediction points scored home'))
cur.execute(description_insert, (prediction_success_away_stat_id, 'prediction_success_away', sort_desc, 'Avg. prediction points scored away'))
cur.execute(description_insert, (prediction_success_total_stat_id, 'prediction_success', sort_desc, 'Avg. prediction points scored'))

con.commit()
print "Completed in %ss" % time.clock()

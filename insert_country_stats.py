from pysqlite2 import dbapi2 as sqlite
import time

def get_seasons():
  """Returns a list of season ids."""

  cur.execute("SELECT id FROM season")
  return [t[0] for t in cur.fetchall()]

def get_season_total(home_stat_id, away_stat_id, total_stat_id, season_id):
  """Calculates overall stats for given season (home and away combined)."""

  total_insert = """INSERT INTO country_stats
                         SELECT %s, country_id, season_id, SUM(sum), SUM(count), CAST(SUM(sum) AS FLOAT) / SUM(count)
                           FROM country_stats
                          WHERE (stat_id = %s OR stat_id = %s)
                            AND season_id = ?
                          GROUP BY country_id"""

  cur.execute(total_insert % (total_stat_id, home_stat_id, away_stat_id), (season_id, ))

def sum_all_seasons(all_seasons_const):
  """Calculates overall stats for all seasons (home and away combined)."""

  total_insert = """INSERT INTO country_stats
                         SELECT stat_id, country_id, '%s', SUM(sum), SUM(count), CAST(SUM(sum) AS FLOAT) / SUM(count)
                           FROM country_stats
                          GROUP BY stat_id, country_id"""

  cur.execute(total_insert % all_seasons_const)


con = sqlite.connect('agcmpl.db')
cur = con.cursor()
time.clock()

cur.execute('DELETE FROM country_stats')

goals_scored_home_insert = """INSERT INTO country_stats
                                   SELECT %s, team.country_id, season_id, SUM(home_result), COUNT(*), CAST(SUM(home_result) AS FLOAT) / COUNT(*)
                                     FROM game, team
                                    WHERE game.home_id = team.id
                                      AND season_id = ?
                                    GROUP BY 2, 3
                                    ORDER BY 2, 3"""

goals_scored_away_insert = """INSERT INTO country_stats
                                   SELECT %s, team.country_id, season_id, SUM(away_result), COUNT(*), CAST(SUM(away_result) AS FLOAT) / COUNT(*)
                                     FROM game, team
                                    WHERE game.away_id = team.id
                                      AND season_id = ?
                                    GROUP BY 2, 3
                                    ORDER BY 2, 3"""

goals_conceded_home_insert = """INSERT INTO country_stats
                                     SELECT %s, team.country_id, season_id, SUM(away_result), COUNT(*), CAST(SUM(away_result) AS FLOAT) / COUNT(*)
                                       FROM game, team
                                      WHERE game.home_id = team.id
                                        AND season_id = ?
                                      GROUP BY 2, 3
                                      ORDER BY 2, 3"""

goals_conceded_away_insert = """INSERT INTO country_stats
                                     SELECT %s, team.country_id, season_id, SUM(home_result), COUNT(*), CAST(SUM(home_result) AS FLOAT) / COUNT(*)
                                       FROM game, team
                                      WHERE game.away_id = team.id
                                        AND season_id = ?
                                      GROUP BY 2, 3
                                      ORDER BY 2, 3"""

country_success_home_insert = """INSERT INTO country_stats
                                   SELECT %s, team.country_id, season_id,
                                          SUM(CASE WHEN game.home_result > game.away_result THEN 3
                                                   WHEN game.home_result = game.away_result THEN 1
                                                   ELSE 0 END),
                                          COUNT(*),
                                          CAST(SUM(CASE WHEN game.home_result > game.away_result THEN 3
                                                        WHEN game.home_result = game.away_result THEN 1
                                                        ELSE 0 END) AS FLOAT) / COUNT(*)
                                     FROM game, team
                                    WHERE game.home_id = team.id
                                      AND season_id = ?
                                    GROUP BY 2, 3
                                    ORDER BY 2, 3"""

country_success_away_insert = """INSERT INTO country_stats
                                   SELECT %s, team.country_id, season_id,
                                          SUM(CASE WHEN game.away_result > game.home_result THEN 3
                                                   WHEN game.home_result = game.away_result THEN 1
                                                   ELSE 0 END),
                                          COUNT(*),
                                          CAST(SUM(CASE WHEN game.away_result > game.home_result THEN 3
                                                        WHEN game.home_result = game.away_result THEN 1
                                                        ELSE 0 END) AS FLOAT) / COUNT(*)
                                     FROM game, team
                                    WHERE game.away_id = team.id
                                      AND season_id = ?
                                    GROUP BY 2, 3
                                    ORDER BY 2, 3"""

predicted_country_success_home_insert = """INSERT INTO country_stats
                                             SELECT %s, team.country_id, season_id, SUM(home_points), COUNT(*), CAST(SUM(home_points) AS FLOAT) / COUNT(*)
                                               FROM game_predictability, team
                                              WHERE game_predictability.home_id = team.id
                                                AND season_id = ?
                                              GROUP BY 2, 3
                                              ORDER BY 2, 3"""

predicted_country_success_away_insert = """INSERT INTO country_stats
                                             SELECT %s, team.country_id, season_id, SUM(away_points), COUNT(*), CAST(SUM(away_points) AS FLOAT) / COUNT(*)
                                               FROM game_predictability, team
                                              WHERE game_predictability.away_id = team.id
                                                AND season_id = ?
                                              GROUP BY 2, 3
                                              ORDER BY 2, 3"""

prediction_success_home_insert = """INSERT INTO country_stats
                                         SELECT %s, team.country_id, season_id, SUM(average), COUNT(*), CAST(SUM(average) AS FLOAT) / COUNT(*)
                                           FROM game_predictability, team
                                          WHERE game_predictability.home_id = team.id
                                            AND season_id = ?
                                          GROUP BY 2, 3
                                          ORDER BY 2, 3"""

prediction_success_away_insert = """INSERT INTO country_stats
                                         SELECT %s, team.country_id, season_id, SUM(average), COUNT(*), CAST(SUM(average) AS FLOAT) / COUNT(*)
                                           FROM game_predictability, team
                                          WHERE game_predictability.away_id = team.id
                                            AND season_id = ?
                                          GROUP BY 2, 3
                                          ORDER BY 2, 3"""

# constants

goals_scored_home_stat_id = 1
goals_scored_away_stat_id = 2
goals_scored_total_stat_id = 3
goals_conceded_home_stat_id = 4
goals_conceded_away_stat_id = 5
goals_conceded_total_stat_id = 6
country_success_home_stat_id = 7
country_success_away_stat_id = 8
country_success_total_stat_id = 9
predicted_country_success_home_stat_id = 10
predicted_country_success_away_stat_id = 11
predicted_country_success_total_stat_id = 12
prediction_success_home_stat_id = 13
prediction_success_away_stat_id = 14
prediction_success_total_stat_id = 15

sort_desc = 0
sort_asc = 1

all_seasons_const = 'all'

# calculate stats and insert into country_stats

seasons = get_seasons()
for season in seasons:
  cur.execute(goals_scored_home_insert % goals_scored_home_stat_id, (season, ))
  cur.execute(goals_scored_away_insert % goals_scored_away_stat_id, (season, ))
  get_season_total(goals_scored_home_stat_id, goals_scored_away_stat_id, goals_scored_total_stat_id, season)

  cur.execute(goals_conceded_home_insert % goals_conceded_home_stat_id, (season, ))
  cur.execute(goals_conceded_away_insert % goals_conceded_away_stat_id, (season, ))
  get_season_total(goals_conceded_home_stat_id, goals_conceded_away_stat_id, goals_conceded_total_stat_id, season)

  cur.execute(country_success_home_insert % country_success_home_stat_id, (season, ))
  cur.execute(country_success_away_insert % country_success_away_stat_id, (season, ))
  get_season_total(country_success_home_stat_id, country_success_away_stat_id, country_success_total_stat_id, season)

  cur.execute(predicted_country_success_home_insert % predicted_country_success_home_stat_id, (season, ))
  cur.execute(predicted_country_success_away_insert % predicted_country_success_away_stat_id, (season, ))
  get_season_total(predicted_country_success_home_stat_id, predicted_country_success_away_stat_id, predicted_country_success_total_stat_id, season)

  cur.execute(prediction_success_home_insert % prediction_success_home_stat_id, (season, ))
  cur.execute(prediction_success_away_insert % prediction_success_away_stat_id, (season, ))
  get_season_total(prediction_success_home_stat_id, prediction_success_away_stat_id, prediction_success_total_stat_id, season)

sum_all_seasons(all_seasons_const)

# insert stat descriptions into country_stats_description

cur.execute('DELETE FROM country_stats_description')
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'goals_scored_home', ?, 'Avg. goals scored home')""", (goals_scored_home_stat_id, 0))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'goals_scored_away', ?, 'Avg. goals scored away')""", (goals_scored_away_stat_id, 0))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'goals_scored', ?, 'Avg. goals scored')""", (goals_scored_total_stat_id, 0))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'goals_conceded_home', ?, 'Avg. goals conceded home')""", (goals_conceded_home_stat_id, 1))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'goals_conceded_away', ?, 'Avg. goals conceded away')""", (goals_conceded_away_stat_id, 1))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'goals_conceded', ?, 'Avg. goals conceded')""", (goals_conceded_total_stat_id, 1))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'country_success_home', ?, 'Avg. points scored home')""", (country_success_home_stat_id, 0))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'country_success_away', ?, 'Avg. points scored away')""", (country_success_away_stat_id, 0))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'country_success', ?, 'Avg. points scored')""", (country_success_total_stat_id, 0))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'predicted_country_success_home', ?, 'Avg. points predicted home')""", (predicted_country_success_home_stat_id, 0))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'predicted_country_success_away', ?, 'Avg. points predicted away')""", (predicted_country_success_away_stat_id, 0))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'predicted_country_success', ?, 'Avg. points predicted')""", (predicted_country_success_total_stat_id, 0))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'prediction_success_home', ?, 'Avg. prediction points scored home')""", (prediction_success_home_stat_id, 0))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'prediction_success_away', ?, 'Avg. prediction points scored away')""", (prediction_success_away_stat_id, 0))
cur.execute("""INSERT INTO country_stats_description
                    VALUES(?, 'prediction_success', ?, 'Avg. prediction points scored')""", (prediction_success_total_stat_id, 0))

con.commit()
print "Completed in %ss" % time.clock()

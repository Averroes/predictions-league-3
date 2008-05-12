from pysqlite2 import dbapi2 as sqlite
import time

def get_total(cur, home_stat_id, away_stat_id, total_stat_id):
  """Calculates overall stats (home and away combined)."""

  total_insert = """INSERT INTO team_stats
                         SELECT %s, team_id, SUM(sum), SUM(count), CAST(SUM(sum) AS FLOAT) / SUM(count)
                           FROM team_stats
                          WHERE stat_id = %s
                             OR stat_id = %s
                          GROUP BY team_id"""

  cur.execute(total_insert % (total_stat_id, home_stat_id, away_stat_id))

con = sqlite.connect('agcmpl.db')
cur = con.cursor()
time.clock()

cur.execute('DELETE FROM team_stats')

goals_scored_home_insert = """INSERT INTO team_stats
                                   SELECT %s, home_id, SUM(home_result), COUNT(*), CAST(SUM(home_result) AS FLOAT) / COUNT(*)
                                     FROM game
                                    GROUP BY 2
                                    ORDER BY 4 DESC, 3 DESC, 1"""

goals_scored_away_insert = """INSERT INTO team_stats
                                   SELECT %s, away_id, SUM(away_result), COUNT(*), CAST(SUM(away_result) AS FLOAT) / COUNT(*)
                                     FROM game
                                    GROUP BY 2
                                    ORDER BY 4 DESC, 3 DESC, 1"""

goals_conceded_home_insert = """INSERT INTO team_stats
                                     SELECT %s, home_id, SUM(away_result), COUNT(*), CAST(SUM(away_result) AS FLOAT) / COUNT(*)
                                       FROM game
                                      GROUP BY 2
                                      ORDER BY 4 DESC, 3 DESC, 1"""

goals_conceded_away_insert = """INSERT INTO team_stats
                                     SELECT %s, away_id, SUM(home_result), COUNT(*), CAST(SUM(home_result) AS FLOAT) / COUNT(*)
                                       FROM game
                                      GROUP BY 2
                                      ORDER BY 4 DESC, 3 DESC, 1"""

team_success_home_insert = """INSERT INTO team_stats
                                   SELECT %s, home_id,
                                          SUM(CASE WHEN game.home_result > game.away_result THEN 3
                                                   WHEN game.home_result = game.away_result THEN 1
                                                   ELSE 0 END),
                                          COUNT(*),
                                          CAST(SUM(CASE WHEN game.home_result > game.away_result THEN 3
                                                        WHEN game.home_result = game.away_result THEN 1
                                                        ELSE 0 END) AS FLOAT) / COUNT(*)
                                     FROM game
                                    GROUP BY 2
                                    ORDER BY 4 DESC"""

team_success_away_insert = """INSERT INTO team_stats
                                   SELECT %s, away_id,
                                          SUM(CASE WHEN game.away_result > game.home_result THEN 3
                                                   WHEN game.home_result = game.away_result THEN 1
                                                   ELSE 0 END),
                                          COUNT(*),
                                          CAST(SUM(CASE WHEN game.away_result > game.home_result THEN 3
                                                        WHEN game.home_result = game.away_result THEN 1
                                                        ELSE 0 END) AS FLOAT) / COUNT(*)
                                     FROM game
                                    GROUP BY 2
                                    ORDER BY 4 DESC"""

predicted_team_success_home_insert = """INSERT INTO team_stats
                                             SELECT %s, home_id, SUM(home_points), COUNT(*), CAST(SUM(home_points) AS FLOAT) / COUNT(*)
                                               FROM game_predictability
                                              GROUP BY 2
                                              ORDER BY 4 DESC"""

predicted_team_success_away_insert = """INSERT INTO team_stats
                                             SELECT %s, away_id, SUM(away_points), COUNT(*), CAST(SUM(away_points) AS FLOAT) / COUNT(*)
                                               FROM game_predictability
                                              GROUP BY 2
                                              ORDER BY 4 DESC"""

prediction_success_home_insert = """INSERT INTO team_stats
                                         SELECT %s, home_id, SUM(average), COUNT(*), CAST(SUM(average) AS FLOAT) / COUNT(*)
                                           FROM game_predictability
                                          GROUP BY 2
                                          ORDER BY 4 DESC"""

prediction_success_away_insert = """INSERT INTO team_stats
                                         SELECT %s, away_id, SUM(average), COUNT(*), CAST(SUM(average) AS FLOAT) / COUNT(*)
                                           FROM game_predictability
                                          GROUP BY 2
                                          ORDER BY 4 DESC"""

# constants

goals_scored_home_stat_id = 1
goals_scored_away_stat_id = 2
goals_scored_total_stat_id = 3
goals_conceded_home_stat_id = 4
goals_conceded_away_stat_id = 5
goals_conceded_total_stat_id = 6
team_success_home_stat_id = 7
team_success_away_stat_id = 8
team_success_total_stat_id = 9
predicted_team_success_home_stat_id = 10
predicted_team_success_away_stat_id = 11
predicted_team_success_total_stat_id = 12
prediction_success_home_stat_id = 13
prediction_success_away_stat_id = 14
prediction_success_total_stat_id = 15

sort_desc = 0
sort_asc = 1

# calculate stats and insert into team_stats

cur.execute(goals_scored_home_insert % goals_scored_home_stat_id)
cur.execute(goals_scored_away_insert % goals_scored_away_stat_id)
get_total(cur, goals_scored_home_stat_id, goals_scored_away_stat_id, goals_scored_total_stat_id)

cur.execute(goals_conceded_home_insert % goals_conceded_home_stat_id)
cur.execute(goals_conceded_away_insert % goals_conceded_away_stat_id)
get_total(cur, goals_conceded_home_stat_id, goals_conceded_away_stat_id, goals_conceded_total_stat_id)

cur.execute(team_success_home_insert % team_success_home_stat_id)
cur.execute(team_success_away_insert % team_success_away_stat_id)
get_total(cur, team_success_home_stat_id, team_success_away_stat_id, team_success_total_stat_id)

cur.execute(predicted_team_success_home_insert % predicted_team_success_home_stat_id)
cur.execute(predicted_team_success_away_insert % predicted_team_success_away_stat_id)
get_total(cur, predicted_team_success_home_stat_id, predicted_team_success_away_stat_id, predicted_team_success_total_stat_id)

cur.execute(prediction_success_home_insert % prediction_success_home_stat_id)
cur.execute(prediction_success_away_insert % prediction_success_away_stat_id)
get_total(cur, prediction_success_home_stat_id, prediction_success_away_stat_id, prediction_success_total_stat_id)

# insert stat descriptions into team_stats_description

cur.execute('DELETE FROM team_stats_description')
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_scored_home', ?, 'Avg. goals scored home')""", (goals_scored_home_stat_id, 0))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_scored_away', ?, 'Avg. goals scored away')""", (goals_scored_away_stat_id, 0))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_scored', ?, 'Avg. goals scored')""", (goals_scored_total_stat_id, 0))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_conceded_home', ?, 'Avg. goals conceded home')""", (goals_conceded_home_stat_id, 1))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_conceded_away', ?, 'Avg. goals conceded away')""", (goals_conceded_away_stat_id, 1))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_conceded', ?, 'Avg. goals conceded')""", (goals_conceded_total_stat_id, 1))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'team_success_home', ?, 'Avg. points scored home')""", (team_success_home_stat_id, 0))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'team_success_away', ?, 'Avg. points scored away')""", (team_success_away_stat_id, 0))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'team_success', ?, 'Avg. points scored')""", (team_success_total_stat_id, 0))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'predicted_team_success_home', ?, 'Avg. points predicted home')""", (predicted_team_success_home_stat_id, 0))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'predicted_team_success_away', ?, 'Avg. points predicted away')""", (predicted_team_success_away_stat_id, 0))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'predicted_team_success', ?, 'Avg. points predicted')""", (predicted_team_success_total_stat_id, 0))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'prediction_success_home', ?, 'Avg. prediction points scored home')""", (prediction_success_home_stat_id, 0))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'prediction_success_away', ?, 'Avg. prediction points scored away')""", (prediction_success_away_stat_id, 0))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'prediction_success', ?, 'Avg. prediction points scored')""", (prediction_success_total_stat_id, 0))

con.commit()
print "Completed in %ss" % time.clock()

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
                                   SELECT %s, team.id, SUM(home_result), COUNT(*), CAST(SUM(home_result) AS FLOAT) / COUNT(*)
                                     FROM team, game
                                    WHERE team.id = game.home_id
                                    GROUP BY game.home_id
                                    ORDER BY 4 DESC, 3 DESC, 1"""

goals_scored_away_insert = """INSERT INTO team_stats
                                   SELECT %s, team.id, SUM(away_result), COUNT(*), CAST(SUM(away_result) AS FLOAT) / COUNT(*)
                                     FROM team, game
                                    WHERE team.id = game.away_id
                                    GROUP BY game.away_id
                                    ORDER BY 4 DESC, 3 DESC, 1"""

goals_conceded_home_insert = """INSERT INTO team_stats
                                   SELECT %s, team.id, SUM(away_result), COUNT(*), CAST(SUM(away_result) AS FLOAT) / COUNT(*)
                                     FROM team, game
                                    WHERE team.id = game.home_id
                                    GROUP BY game.home_id
                                    ORDER BY 4 DESC, 3 DESC, 1"""

goals_conceded_away_insert = """INSERT INTO team_stats
                                   SELECT %s, team.id, SUM(home_result), COUNT(*), CAST(SUM(home_result) AS FLOAT) / COUNT(*)
                                     FROM team, game
                                    WHERE team.id = game.away_id
                                    GROUP BY game.away_id
                                    ORDER BY 4 DESC, 3 DESC, 1"""

goals_scored_home_stat_id = 1
goals_scored_away_stat_id = 2
goals_scored_total_stat_id = 3
goals_conceded_home_stat_id = 4
goals_conceded_away_stat_id = 5
goals_conceded_total_stat_id = 6

cur.execute(goals_scored_home_insert % goals_scored_home_stat_id)
cur.execute(goals_scored_away_insert % goals_scored_away_stat_id)
get_total(cur, goals_scored_home_stat_id, goals_scored_away_stat_id, goals_scored_total_stat_id)

cur.execute(goals_conceded_home_insert % goals_conceded_home_stat_id)
cur.execute(goals_conceded_away_insert % goals_conceded_away_stat_id)
get_total(cur, goals_conceded_home_stat_id, goals_conceded_away_stat_id, goals_conceded_total_stat_id)

cur.execute('DELETE FROM team_stats_description')
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_scored_home', 'Avg. goals scored home')""", (goals_scored_home_stat_id, ))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_scored_away', 'Avg. goals scored away')""", (goals_scored_away_stat_id, ))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_scored', 'Avg. goals scored')""", (goals_scored_total_stat_id, ))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_conceded_home', 'Avg. goals conceded home')""", (goals_conceded_home_stat_id, ))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_conceded_away', 'Avg. goals conceded away')""", (goals_conceded_away_stat_id, ))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_conceded', 'Avg. goals conceded')""", (goals_conceded_total_stat_id, ))

con.commit()
print "Completed in %ss" % time.clock()

from pysqlite2 import dbapi2 as sqlite

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

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
goals_conceded_home_stat_id = 3
goals_conceded_away_stat_id = 4

cur.execute(goals_scored_home_insert % goals_scored_home_stat_id)
cur.execute(goals_scored_away_insert % goals_scored_away_stat_id)
cur.execute(goals_conceded_home_insert % goals_conceded_home_stat_id)
cur.execute(goals_conceded_away_insert % goals_conceded_away_stat_id)

cur.execute('DELETE FROM team_stats_description')
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_scored_home', 'Avg. goals scored home')""", (goals_scored_home_stat_id, ))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_scored_away', 'Avg. goals scored away')""", (goals_scored_away_stat_id, ))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_conceded_home', 'Avg. goals conceded home')""", (goals_conceded_home_stat_id, ))
cur.execute("""INSERT INTO team_stats_description
                    VALUES(?, 'goals_conceded_away', 'Avg. goals conceded away')""", (goals_conceded_away_stat_id, ))

con.commit()

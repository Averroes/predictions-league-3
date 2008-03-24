from pysqlite2 import dbapi2 as sqlite

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

cur.executescript("""CREATE TABLE IF NOT EXISTS player
                    ( id   INTEGER PRIMARY KEY,
                      name TEXT
                    );""")

cur.executescript("""CREATE TABLE IF NOT EXISTS round
                    ( season_id      TEXT,
                      id             INTEGER,
                      competition_id INTEGER,
                      PRIMARY KEY(season_id, id)
                    );""")

cur.executescript("""CREATE TABLE IF NOT EXISTS competition
                    ( id   INTEGER PRIMARY KEY,
                      name TEXT
                    );""")

cur.executescript("""CREATE TABLE IF NOT EXISTS team
                    ( id          INTEGER PRIMARY KEY,
                      name        TEXT,
                      country_id  INTEGER
                    );""")

cur.executescript("""CREATE TABLE IF NOT EXISTS game
                    ( id          INTEGER PRIMARY KEY,
                      round_id    INTEGER,
                      season_id   TEXT,
                      home_id     INTEGER,
                      away_id     INTEGER,
                      home_result INTEGER,
                      away_result INTEGER
                    );""")

cur.executescript("""CREATE TABLE IF NOT EXISTS prediction
                    ( id        INTEGER PRIMARY KEY,
                      player_id INTEGER,
                      game_id   INTEGER,
                      home      INTEGER,
                      away      INTEGER,
                      points    INTEGER
                    );""")

cur.executescript("""CREATE TABLE IF NOT EXISTS season
                    ( id    TEXT PRIMARY KEY,
                      title TEXT
                    );""")

cur.executescript("""CREATE TABLE IF NOT EXISTS country
                    ( id    INTEGER PRIMARY KEY,
                      name  TEXT,
                      code  TEXT
                    );""")

con.commit()

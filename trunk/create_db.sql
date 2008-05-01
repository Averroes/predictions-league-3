CREATE TABLE IF NOT EXISTS competition
( id   INTEGER PRIMARY KEY,
  name TEXT
);

CREATE TABLE IF NOT EXISTS country
( id    INTEGER PRIMARY KEY,
  name  TEXT,
  code  TEXT
);

CREATE TABLE IF NOT EXISTS country_stats
( stat_id    INTEGER,
  country_id INTEGER,
  sum        INTEGER,
  count      INTEGER,
  average    FLOAT,
  PRIMARY KEY(stat_id, country_id)
);

CREATE INDEX country_stats_idx ON country_stats(country_id);

CREATE TABLE IF NOT EXISTS country_stats_description
( id          INTEGER PRIMARY KEY,
  title       TEXT,
  description TEXT
);

CREATE TABLE IF NOT EXISTS game
( id          INTEGER PRIMARY KEY,
  round_id    INTEGER,
  season_id   TEXT,
  home_id     INTEGER,
  away_id     INTEGER,
  home_result INTEGER,
  away_result INTEGER
);

CREATE TABLE IF NOT EXISTS player
( id   INTEGER PRIMARY KEY,
  name TEXT
);

CREATE UNIQUE INDEX player_name_idx ON player(name);

CREATE TABLE IF NOT EXISTS prediction
( id        INTEGER PRIMARY KEY,
  player_id INTEGER,
  game_id   INTEGER,
  home      INTEGER,
  away      INTEGER,
  points    INTEGER
);

CREATE TABLE IF NOT EXISTS round
( season_id      TEXT,
  id             INTEGER,
  competition_id INTEGER,
  PRIMARY KEY(season_id, id)
);

CREATE TABLE IF NOT EXISTS season
( id    TEXT PRIMARY KEY,
  title TEXT
);

CREATE TABLE IF NOT EXISTS team
( id          INTEGER PRIMARY KEY,
  name        TEXT,
  country_id  INTEGER
);

CREATE UNIQUE INDEX team_name_idx ON team(name);

CREATE TABLE IF NOT EXISTS team_stats
( stat_id INTEGER,
  team_id INTEGER,
  sum     INTEGER,
  count   INTEGER,
  average FLOAT,
  PRIMARY KEY(stat_id, team_id)
);

CREATE INDEX team_stats_idx ON team_stats(team_id);

CREATE TABLE IF NOT EXISTS team_stats_description
( id          INTEGER PRIMARY KEY,
  title       TEXT,
  description TEXT
);

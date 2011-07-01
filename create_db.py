from sqlite3 import dbapi2 as sqlite

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

sql_files = ['create_db.sql', 'competitions.sql', 'stages.sql']

for sql_file in sql_files:
  f = open(sql_file, 'r')
  script = f.read()
  f.close()
  cur.executescript(script)

con.commit()

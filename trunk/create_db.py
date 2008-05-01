from pysqlite2 import dbapi2 as sqlite

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

f = open("create_db.sql", "r")
script = f.read()

cur.executescript(script)

con.commit()

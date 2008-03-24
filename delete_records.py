from pysqlite2 import dbapi2 as sqlite

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

cur.execute('DELETE FROM player')
cur.execute('DELETE FROM season')
cur.execute('DELETE FROM round')
cur.execute('DELETE FROM game')
cur.execute('DELETE FROM prediction')
cur.execute('DELETE FROM team')
cur.execute('DELETE FROM country')

con.commit()

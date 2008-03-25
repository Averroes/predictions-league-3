from pysqlite2 import dbapi2 as sqlite

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

cur.execute("""SELECT 'SELECT COUNT(*) FROM ' || name, name
                 FROM sqlite_master
                WHERE type = 'table'
                ORDER BY 2""")

print 'table            count'
print '----------------------'
for query in cur.fetchall():
  cur.execute(query[0])
  print '%-15s %6d' % (query[1], cur.fetchone()[0])

con.commit()

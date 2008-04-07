from pysqlite2 import dbapi2 as sqlite

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

cur.execute("""SELECT name
                 FROM sqlite_master
                WHERE type = 'table'
                ORDER BY 1""")

print 'table                      count'
print '--------------------------------'
for table in cur.fetchall():
  cur.execute('SELECT COUNT(*) FROM %s' % table[0])
  print '%-25s %6d' % (table[0], cur.fetchone()[0])

con.commit()

from pysqlite2 import dbapi2 as sqlite

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

cur.execute("""SELECT name
                 FROM sqlite_master
                WHERE type = 'table'
                ORDER BY 1""")

print 'table                              count'
print '----------------------------------------'
total = 0
for table in cur.fetchall():
  cur.execute('SELECT COUNT(*) FROM %s' % table[0])
  count = cur.fetchone()[0]
  total += count
  print '%-32s %7d' % (table[0], count)

print '----------------------------------------'
print '%-32s %7d' % ("total row count", total)

con.commit()

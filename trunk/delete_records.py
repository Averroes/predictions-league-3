from sqlite3 import dbapi2 as sqlite

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

cur.execute("""SELECT name
                 FROM sqlite_master
                WHERE type = 'table'
                ORDER BY 1""")

for table in cur.fetchall():
  count = cur.execute('DELETE FROM %s WHERE 1 = 1' % table[0]).rowcount
  print 'Deleted %6d records from %-15s' % (count, table[0])

con.commit()

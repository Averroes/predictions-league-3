from pysqlite2 import dbapi2 as sqlite

con = sqlite.connect('agcmpl.db')
cur = con.cursor()

cur.execute("""SELECT 'DELETE FROM ' || name || ' WHERE 1 = 1', name
                 FROM sqlite_master
                WHERE type = 'table'
                ORDER BY 2""")

for delete_statement in cur.fetchall():
  count = cur.execute(delete_statement[0]).rowcount
  print 'Deleted %6d records from %-15s' % (count, delete_statement[1])

con.commit()

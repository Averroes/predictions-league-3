from sqlite3 import dbapi2 as sqlite

con = sqlite.connect('agcmpl.db')
full_dump = '\n'.join([line for line in con.iterdump()])
with open('dump.sql', 'w') as f:
  f.writelines(full_dump)

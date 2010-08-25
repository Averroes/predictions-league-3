from pysqlite2 import dbapi2 as sqlite3
import os

con = sqlite3.connect('agcmpl.db')
full_dump = os.linesep.join([line for line in con.iterdump()])
f = open('dump.sql', 'w')
f.writelines(full_dump)
f.close()

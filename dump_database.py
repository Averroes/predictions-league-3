from sqlite3 import dbapi2 as sqlite
import os

con = sqlite.connect('agcmpl.db')
full_dump = os.linesep.join([line for line in con.iterdump()])
f = open('dump.sql', 'w')
f.writelines(full_dump)
f.close()

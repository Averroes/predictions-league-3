import os, time

i = 0
time.clock()
for root, dirs, files in os.walk('stats'):
  if root.find('.svn') > -1: # ignore SVN folders
    continue
  print "Deleting files from %s..." % root
  for name in files:
    os.remove(os.path.join(root, name))
    i += 1

print "Deleted %d files in %ss" % (i, time.clock())

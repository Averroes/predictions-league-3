import re

pattern = re.compile("(?P<home>^.*)\sv\s(?P<away>.*$)")
fr = open('games.txt', 'r')
fw = open('games_reversed.txt', 'w')
i = 0

for line in fr:
  found = re.match(pattern, line)
  if found:
    fw.write(found.group('away') + ' v ' + found.group('home') + '\n')
    i += 1

fw.close()
fr.close()
print 'Reversed %d games.' % i

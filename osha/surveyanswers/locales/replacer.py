#!/opt/python/python-2.4/bin/python

import os
bad = "’"
good = "?"

fname = "osha.surveyanswers.po"
cwd = os.getcwd()
print cwd

langdirs = [x for x in os.listdir('.') if len(x)==2]
for ld in langdirs:
  path = "%s/%s/LC_MESSAGES" %(cwd, ld)
  print path
  cnt = 0
  fh = open("%s/%s" %(path, fname), 'r')
  data = fh.read()
  fh.close()

  new_lines = list()
  lines = data.split('\n')
  for li in lines:
    if li.find(bad) > 0 and li.startswith('msgid'):
      li = li.replace(bad, good)
      cnt += 1
    new_lines.append(li)

  fh = open("%s/%s" %(path, fname), 'w')
  fh.write('\n'.join(new_lines))
  fh.close()
  print "%d replacements done" %cnt

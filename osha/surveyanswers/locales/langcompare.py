#!/opt/python/python-2.4/bin/python

import os
import sys
from popen2 import popen3

lang = sys.argv[1]
pot = len(sys.argv)>2 and sys.argv[2] or "statics.pot"
fname = "osha.surveyanswers.po"

po_file = "%s/LC_MESSAGES/%s" %( lang, fname)

if not os.path.exists(po_file):
    print "ERROR, file not found for language '%s'" %lang
    sys.exit(0)

pot_file = "%s" % pot
if not os.path.exists(pot_file):
    print "ERROR, pot file not found for '%s'" %pot
    sys.exit(0)

cmd = "msgcmp %s %s" %(po_file, pot_file)

stout, stdin, stderr = popen3(cmd) 
err = stderr.read()
lines = err.split('\n')

check1 = "this message is used but not defined"
check2 = "but this definition is similar"

result = [x for x in lines if check1 in x or check2 in x]

print "\n".join(result)

#!/opt/python/python-2.4/bin/python

import os
import sys
import time
from popen2 import popen3

lang = sys.argv[1]
pot = len(sys.argv)>2 and sys.argv[2] or "statics.pot"
fname = "osha.surveyanswers.po"
missing_name = "missing_%s.po" % lang

po_file = "%s/LC_MESSAGES/%s" % (lang, fname)

if not os.path.exists(po_file):
    print "ERROR, file not found for language '%s'" %lang
    sys.exit(0)

missing_file = "%s/LC_MESSAGES/%s" % (lang, missing_name)

if not os.path.exists(missing_file):
    print "ERROR, 'missing' file not found for language '%s'" %lang
    sys.exit(0)

pot_file = "%s" % pot
if not os.path.exists(pot_file):
    print "ERROR, pot file not found for '%s'" %pot
    sys.exit(0)


tmp_name = "TMP_LANG_CHECK"
cmd = "msgcat -o %s %s %s" % (tmp_name, po_file, missing_file)
print "executing\n", cmd
stout, stdin, stderr = popen3(cmd)

time.sleep(2)

cmd = "msgcmp %s %s" %(tmp_name, pot_file)
print "executing\n", cmd
stout2, stdin2, stderr2 = popen3(cmd) 
err = stderr2.read()

lines = err.split('\n')

check1 = "this message is used but not defined"
check2 = "but this definition is similar"

result = [x for x in lines if check1 in x or check2 in x]

print "\nThe following missing entries were found"

print "\n".join(result)

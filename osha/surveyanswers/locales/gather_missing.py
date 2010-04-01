#!/opt/python/python-2.4/bin/python

import os
from popen2 import popen3

fname = "missing_%s.po"
cwd = os.getcwd()
print cwd

missing_dir = "%s/missing/" %cwd
if not os.path.exists(missing_dir):
    os.mkdir(missing_dir)
    print "created %s" % missing_dir

langdirs = [x for x in os.listdir('.') if len(x)==2]
for ld in langdirs:
    path = "%s/%s/LC_MESSAGES" %(cwd, ld)
    po_file = "%s/%s" % (path, fname) %ld

    if not os.path.exists(po_file):
        print "ERROR, file not found for language '%s'" %ld
        continue

    cmd = "cp %s %s" %(po_file, missing_dir)
    stout, stdin, stderr = popen3(cmd) 
    err = stderr.read()
    if err:
        print "ERROR in copying for %s:\n%s" % (ld, err)

cmd = "tar cvfz missing_translations.tgz missing/"
stout, stdin, stderr = popen3(cmd) 
err = stderr.read()
if err:
    print "ERROR in creating tar:\n%s" %err
else:
    print "created tgz with missing files"
#delete db
#in buildout, run make_db.py
#in buildout, run $DBTOOL db < db_setup.sql
export PGPASSWORD="postgres"
DBTOOL="psql -d global_portal_db -h 127.0.0.1 -U postgres -f "
PYTHON="./bin/python"
$PYTHON make_db.py
echo .
$DBTOOL db_setup.sql
echo .
$PYTHON questions.py > questions.sql
echo .
$DBTOOL questions.sql
echo .
$PYTHON questions2.py > questions2.sql
echo .
$DBTOOL questions2.sql
echo .
$PYTHON groups.py > groups.sql
echo .
$DBTOOL groups.sql
echo .
$DBTOOL step1.sql | grep '|' > step1.txt
echo .
$PYTHON step2.py > step2.sql
echo .
$DBTOOL step2.sql  | egrep '[0-9]' | grep -v row > step2.txt
echo .
$PYTHON step3.py > step3.sql
echo .
$DBTOOL step3.sql
echo .
$DBTOOL special.sql
echo .


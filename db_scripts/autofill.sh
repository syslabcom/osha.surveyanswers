#delete db
#in buildout, run make_db.py
#in buildout, run $DBTOOL db < db_setup.sql
export PGPASSWORD="postgres"
DBTOOL="psql -d global_portal_db -h 127.0.0.1 -U postgres -f "
PYTHON="./bin/python"
$PYTHON make_db.py
echo "db_setup.sql"
$DBTOOL db_setup.sql
echo "questions.py"
$PYTHON questions.py > questions.sql
echo "questions.sql"
$DBTOOL questions.sql
echo "questions2.py"
$PYTHON questions2.py > questions2.sql
echo "questions2.sql"
$DBTOOL questions2.sql
echo "groups.py"
$PYTHON groups.py > groups.sql
echo "groups.sql"
$DBTOOL groups.sql
echo "step1.sql"
$DBTOOL step1.sql | grep '|' > step1.txt
echo "step2.py"
$PYTHON step2.py > step2.sql
echo "step2.sql"
$DBTOOL step2.sql  | egrep '[0-9]' | grep -v row > step2.txt
echo "step3.py"
$PYTHON step3.py > step3.sql
echo "step3.sql"
$DBTOOL step3.sql
echo "special.sql"
$DBTOOL special.sql
echo "Done"

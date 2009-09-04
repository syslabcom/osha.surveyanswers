#delete db
#in buildout, run make_db.py
#in buildout, run sqlite3 db < db_setup.sql
rm ~/projects/osha_git/buildout/beeer
echo .
python make_db.py
echo .
sqlite3 ~/projects/osha_git/buildout/beeer < db_setup.sql
echo .
python questions.py > questions.sql
echo .
sqlite3 ~/projects/osha_git/buildout/beeer < questions.sql
echo .
./bin/python questions2.py > questions2.sql
echo .
sqlite3 ~/projects/osha_git/buildout/beeer < questions2.sql
echo .
python groups.py > groups.sql
echo .
sqlite3 ~/projects/osha_git/buildout/beeer < groups.sql
echo .
sqlite3 ~/projects/osha_git/buildout/beeer < step1.sql > step1.txt
echo .
python step2.py > step2.sql
echo .
sqlite3 ~/projects/osha_git/buildout/beeer < step2.sql > step2.txt
echo .
python step3.py > step3.sql
echo .
sqlite3 ~/projects/osha_git/buildout/beeer < step3.sql
echo .
sqlite3 ~/projects/osha_git/buildout/beeer < special.sql
echo .


#delete db
#in buildout, run make_db.py
#in buildout, run db_tool db < db_setup.sql
db_tool = sqlite3
rm ~/projects/osha_git/buildout/surveyanswers
echo .
python make_db.py
echo .
db_tool ~/projects/osha_git/buildout/surveyanswers < db_setup.sql
echo .
python questions.py > questions.sql
echo .
db_tool ~/projects/osha_git/buildout/surveyanswers < questions.sql
echo .
./bin/python questions2.py > questions2.sql
echo .
db_tool ~/projects/osha_git/buildout/surveyanswers < questions2.sql
echo .
python groups.py > groups.sql
echo .
db_tool ~/projects/osha_git/buildout/surveyanswers < groups.sql
echo .
db_tool ~/projects/osha_git/buildout/surveyanswers < step1.sql > step1.txt
echo .
python step2.py > step2.sql
echo .
db_tool ~/projects/osha_git/buildout/surveyanswers < step2.sql > step2.txt
echo .
python step3.py > step3.sql
echo .
db_tool ~/projects/osha_git/buildout/surveyanswers < step3.sql
echo .
db_tool ~/projects/osha_git/buildout/surveyanswers < special.sql
echo .


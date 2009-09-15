prefix = 1

for line in file('step1.txt'):
    if prefix:
        prefix -= 1
	continue
    row, answer = line.split('|')
    if row.strip() in ['est_wei2', 'est_wei1', 'emp_wei1', 'emp_wei2']:
    	continue
    print "select id from questions where question_field = \'%s\';" % row.strip()
    print "select count(id) as count, country from responses where %s & %s = %s group by country order by count;" % (row, answer.strip(), answer.strip())
    print "select count(id) as count, country, country from responses group by country;"
print "select count(id) as count from responses;"

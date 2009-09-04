for line in file('step1.txt'):
    row, answer = line.split('|')
    print "select id from questions where question_field = \"%s\";" % row
    print "select count(id) as count, country from responses where %s & %s group by country order by count;" % (row, answer.strip())
    print "select count(id) as count, country, id from responses group by country;"
print "select count(id) as count from responses;"

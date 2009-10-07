import re
import random

country_mapping = {
12:3,
1:5,
31:7,
46:8,
32:44,
33:9,  
2:10,
34:11,
6:12,
7:13,
3:14,
4:15,
35:16,
8:18,
9:19,
36:20,
37:22,
10:23,
38:25,
11:29,
39:31,
13:32,
40:33,
41:36,
42:37,
5:38,
14:39,
43:45,
15:42,
51:40,
52:30,
}
percent_questions = ['mm401', 'mm405', 'mm400', 'rev1_1di']
questions = []
finder = re.compile('([^ ]+) +[^ ]+ +([^ ]+) +([^ ]+).*([01]+)')
for line in file('questions.txt'):
    data = list(finder.findall(line)[0])
    data[0] = data[0].replace(".", "")
    data[1] = int(data[1]) - 1
    data[2] = int(data[2])
    questions.append(data)

groups = ['group %i' % i for i in range(10)]

print ("delete from questions;")
for question in questions:
    options = dict(
        question_field = question[0],
        question = question[0],
        question_group = random.sample(groups, 1)[0],
        is_country = str(question[0] == 'country' and '1' or '0'),
        is_designator = str(question[0] in ('sec3', 'size_5') and '1' or '0'),
        type = question[0].lower() in percent_questions and '2' or '1',
        show_which = question[0].lower() in percent_questions and '0' or '2',
        show_which_text = 'yes', 
        hide = question[3])
    print 'insert into questions (question_field, question, question_group, is_country, is_designator, type, show_which, show_which_text, hide_question) values(\'%(question_field)s\', \'%(question)s\', \'%(question_group)s\', %(is_country)s, %(is_designator)s, %(type)s, %(show_which)s, \'%(show_which_text)s\', %(hide)s);' % options
    if options['is_country'] == '1':
        print 'update answer_meanings set question_id = (select id from questions where question_field = \'%s\') where question_id = 0;' % options['question_field']
        print 'delete from answer_meanings where question_id != (select id from questions where question_field = \'%s\');' % options['question_field']

print 'drop table responses;'
print 'create table responses (id SERIAL PRIMARY KEY, %s);' % (", ".join(["%s %s" % (x[0], x[0].lower() in percent_questions and 'FLOAT' or 'INTEGER') for x in questions[:-4]] + ["%s FLOAT" % x[0] for x in questions[-4:]]))
counter = 0
for line in file('ESENER2009_20090924_EUOSHA.dat'):
    sql_question = []
    sql_answer = []
    for question in questions:
        sql_question.append(question[0])
        answer = line[question[1]:question[2]].strip()
        if answer.startswith('.'):
            answer = '0' + answer
        answer = answer.replace(',', '')
        if answer == '':
            answer = 0
        if question[0] == 'country':
            answer = str(country_mapping[int(answer)])
        else:
            try:
                if question[0].lower() not in percent_questions + ['country2']:
                    answer = str(2**int(answer))
                else:
                    answer = '%02.2f' % float(answer)
            except:
                pass
        sql_answer.append(answer)
    print 'insert into responses(%s) values (%s);' % (", ".join(sql_question), ", ".join(['\'%s\'' % x for x in sql_answer]))
    

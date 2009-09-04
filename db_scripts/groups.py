old_group =group = 'dummy'
questions = []
for line in file('groups.txt'):
    if not (line.startswith('ER') or line.startswith('MM')):
        old_group = group
        group = line.strip()
        for question in questions:
            print "update questions set question_group = \"%s\" where question_field LIKE \"%s%%\";" % (old_group, question)
        questions = []
    else:
        questions.append(line.strip())

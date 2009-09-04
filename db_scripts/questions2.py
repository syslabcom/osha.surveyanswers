import xlrd

xls_file = xlrd.open_workbook('questions.xls')
sheet = xls_file.sheet_by_name('TRANSLATION')

questions = {}
new_state = state = 'end_question'

for row_id in range(sheet.nrows):
    row = sheet.row(row_id)
    if state == 'end_question':
        if row[1].value.startswith('ER') or row[1].value.startswith('MM'):
            if sheet.row(row_id + 4)[2].value == 1:
                new_state = 'start_multiquestion'
                multi_questions_prefix = row[1].value
                multi_question_question = row[2].value
                multi_questions = {}
            else:
                question = {}
                questions[row[1].value] = (question, row[2].value)
                new_state = 'start_question'
    elif state == 'start_question':
        for cell_pos in range(len(row)):
            cell = row[cell_pos].value
            if row[cell_pos].ctype == 1 and cell.startswith('(') and cell.endswith(')') and cell_pos > 2: 
                answer_key_position = cell_pos
                new_state = 'start_answers'
    elif state == 'start_multiquestion':
        if row[3].value:
            multi_question_answers = []
            multi_question_answer_positions = []
            for cell_pos in range(4, 20):
                if row[cell_pos].value:
                    multi_question_answers.append(row[cell_pos].value)
                    multi_question_answer_positions.append(cell_pos)
            new_state = 'start_multiquestion_answers_jump_one_line'
                    
    elif state == 'start_answers':
        if row[2].value:
            try:
                key = row[answer_key_position].value
                try:
                    key = int(key)
                except:
                    key = int(key.strip().strip(','))
                question[key] = row[2].value
            except:
                import pdb;pdb.set_trace()
        else:
            new_state = 'end_question'
    elif state == 'start_multiquestion_answers_jump_one_line':
        new_state = 'start_multiquestion_answers'
    elif state == 'start_multiquestion_answers':
        if row[2].value:
            question = {}
            questions[multi_questions_prefix + str(int(row[2].value))] = (question, " ".join([multi_question_question, row[3].value]))
            for i in range(len(multi_question_answer_positions)):
                try:
                    question[int(row[multi_question_answer_positions[i]].value)] = \
                        multi_question_answers[i]
                except:
                    import pdb;pdb.set_trace()

        else:
            new_state = 'end_question'
    if new_state != state:
        state = new_state

for key, (answers, question_text) in questions.items():
    try:
        print ("update questions set question = \"%s\" where question_field = \"%s\";" % (question_text, key)).encode('ascii', 'replace')
    except:
        import pdb;pdb.set_trace()
    i = 0
    no_answer_msg_exists = True
    for key2, answer in answers.items():
        if key2 == 0:
            no_answer_msg_exists = False
        i += 1
        print ("insert into answer_meanings (question_id, answer_bit, answer_text, position) values ((select id from questions where question_field = \"%s\"), %i, \"%s\", %i);" % (key, 2 ** key2, answer, i)).encode("ascii", 'replace')
    if no_answer_msg_exists:
        print "insert into answer_meanings (question_id, answer_bit, answer_text, position) values ((select id from questions where question_field = \"%s\"), 1, \"No answer given\", 99);" % key

import re

from zope.component import adapts #@UnresolvedImport
from zope.component import getUtility #@UnresolvedImport
from zope.interface import implements

import sqlalchemy as sa #@UnresolvedImport

from collective.lead.interfaces import IDatabase

from osha.surveyanswers.interfaces import ISurvey, ISurveyDatabase

questionFilter = lambda x: re.compile('^question_[1-9][0-9]{0,1}$').match(x)

class SurveyDatabase(object):
    adapts(ISurvey)
    implements(ISurveyDatabase)
    ID_ROW = 0
    ANSWER_ROW_ID = 1
    NAME_ROW = 2
    GROUP_ROW = 3
    country_row = 'country'
    questionDicter = lambda ign, x: {'text' : x[SurveyDatabase.NAME_ROW], 
                                'question_id': x[SurveyDatabase.ID_ROW],
                                'answer_row_name' : x[SurveyDatabase.ANSWER_ROW_ID]}
    
    def __init__(self, context):
        self.context = context 

    @property
    def responses(self):
        if not hasattr(self, '_responses'):
            self._responses = sa.Table('responses', self.meta, autoload=True)
        return self._responses
    
    @property
    def questions(self):
        if not hasattr(self, '_questions'):
            self._questions = sa.Table('questions', self.meta, autoload=True)
        return self._questions
    
    @property
    def map_data(self):
        if not hasattr(self, '_map_data'):
            self._map_data = sa.Table('map_data', self.meta, autoload=True)
        return self._map_data 
    
    @property
    def connection(self):
        if not hasattr(self, '_connection'):
            db_util = getUtility(IDatabase, "osha.database")
            self._connection = db_util.connection
        return self._connection

    @property
    def meta(self):
        if not hasattr(self, '_meta'):
            self._meta = sa.MetaData()
            self.meta.bind = self.connection
        return self._meta
        
    @property
    def answer_meanings(self):
        if not hasattr(self, '_answer_meanings'):
            self._answer_meanings = sa.Table('answer_meanings', self.meta, autoload=True)
        return self._answer_meanings
        
    def _query(self, stmt, **kwargs):
        return self.connection.engine.execute(stmt, **kwargs).fetchall()
            
    def getAllQuestions(self):
        """
        Return a List of dictionaries
        The dictionary contains a name, that is a human readable group name
        and questions, which is a list of dictionaries, representing questions
        of the group
        The question dictionary has the attributes
        text which contains the human readable question text
        question_id which contains the numeric id of the question row in the database
        answer_row_name which contains the row name in the answers db for the given question
        """
        all_questions = self.connection.execute(self.questions.select('hide_question=0')).fetchall()
        def reducer(retval, question):
            found = False
            for group in retval:
                if group['name'] == question[self.GROUP_ROW]:
                    group['questions'].append(self.questionDicter(question))
                    found = True
            if not found:
                retval.append({'name' : question[self.GROUP_ROW], 
                               'questions': [self.questionDicter(question)]})
            return retval
        return reduce(reducer, all_questions, [])
            
    def hasQuestion(self, question_id):
        """
        Return whether a question with the given question_id exists
        """
        try:
            question_exists = self.connection.execute(self.questions.select('id=:question').params(question=int(question_id))).fetchall() 
            return question_exists
        except ValueError:
            return False
    
    def getQuestion(self, question_id):
        """
        Return common information about a question:
        text which contains the human readable question text
        question_id which contains the numeric id of the question row in the database
        answer_row_name which contains the row name in the answers db for the given question
        """
        question = self.connection.execute(self.questions.select('id=:question').params(question=question_id)).fetchall()[0]
        return self.questionDicter(question)
    
    def getAnswerRow(self, question_id):
        """
        Return the row name for a given question in the answers table
        """ 
        return self.getQuestion(question_id)['answer_row_name']
    
    def getMapInfo(self, question_id):
        """
        Return range information to beautify a map for a given question
        """
        question = self.connection.execute(self.map_data.select('question_id=:question_id').params(question_id=question_id)).fetchall()[0]
        try:
            answer_text = self._query("select am.answer_text from questions as q, answer_meanings as am where q.id = %(question_id)s and am.question_id = q.id and am.answer_bit & q.show_which = q.show_which", question_id = question_id)[0][0]
        except IndexError:
            answer_text = self._query("select am.answer_text from questions as q, answer_meanings as am where q.id = %(question_id)s and am.question_id = q.id and am.answer_bit & 1 = 1", question_id = question_id)[0][0]
        retval = {}
        retval['rng1'] = question[2]
        retval['rng1_msg'] = question[3]
        retval['rng2'] = question[4]
        retval['rng2_msg'] = question[5]
        retval['rng3'] = question[6]
        retval['rng3_msg'] = question[7]
        retval['show_which_answer'] = answer_text
         
        return retval
    
    def getOrderedAnswerMeanings(self, question):
        question_id = self.getQuestionIdFromRowName(question)
        for country in self._query("select answer_text from answer_meanings where question_id = %(question_id)s order by position", question_id = question_id):
            yield country[0]
            
    def getCountryName(self, country_id):
        return self._query("select am.answer_text from answer_meanings as am, questions as q where q.question_field = \'%s\' and am.question_id = q.id and am.answer_bit = %%(country)s" % self.country_row, country = country_id)[0][0]
            
    def getQuestionIdFromRowName(self, row_name):
        return self._query("select id from questions where question_field = %(question_field)s", question_field = row_name)[0][0]
    
    def getAnswersForExport(self, question_id):
        params = {'answer_row' : self.getAnswerRow(question_id), 
                  'country_row' : self.country_row}
        data = self._query('select r.%(country_row)s, sum(est_wei2), r.%(answer_row)s from responses as r group by r.%(answer_row)s, r.%(country_row)s' % params)
        answer_meanings = self._query('select answer_bit, answer_text from answer_meanings where question_id = %(question_id)s order by position', question_id = question_id)
        countries = self._query('select am.answer_bit, am.answer_text from answer_meanings as am, questions as q where q.question_field = \'%(country_row)s\' and am.question_id = q.id order by position' % params)
        datasets = {}
        totals = {}
        for row in data:
            if not datasets.has_key(row[0]):
                datasets[row[0]] = {}
            answers = datasets[row[0]]
            answers[row[2]] = answers.get(row[2], 0) + row[1]
            if int(row[2]) != 1:
                totals[row[0]] = totals.get(row[0], 0) + row[1]
        row_head = [x[1] for x in answer_meanings]
        for country_id, total in totals.items():
            row = datasets[country_id]
            for answer_name, answer_count in row.items():
                row[answer_name] = answer_count / float(total)
        yield ["Country"] + row_head
        for country in countries:
            if not datasets.has_key(country[0]):
                continue
            values = datasets[country[0]]
            yield [country[1]] + [values.get(x[0], 0) for x in answer_meanings]
            
    def getAnswersFor(self, question_id):
        """
        Return a dictionary of relative percentages to show on map
        """
        answer_map = self.connection.engine.execute('select show_which from questions where id = %(question_id)s', question_id=question_id).fetchall()[0][0]
        where_stmt = '%s & %s = %s' % (self.getAnswerRow(question_id), answer_map, answer_map)
        yes_intermed = self._query('select %(country_row)s, sum(est_wei2) from responses where %(where)s group by %(country_row)s order by %(country_row)s' % ({'country_row' : self.country_row, 'where' : where_stmt})) # save sql statement
        all = self._query('select %(country_row)s, sum(est_wei2) from responses where %(question_row)s != 1 group by %(country_row)s order by %(country_row)s' % \
            {'country_row' : self.country_row, 
            'question_row' : self.getAnswerRow(question_id)})
        yes = []
        for one_of_all in all:
            found = False
            for one_of_yes in yes_intermed:
                if one_of_all[0] == one_of_yes[0]:
                    found = True
                    yes.append(one_of_yes)
            if not found:
                yes.append((one_of_all[0], 0))
        # Map and reduce in simple
        return dict(map(lambda ((country, yes), (i, all)): 
                            (country, 
                             (float(yes) / all)
                            ),
                         zip(yes, all)))
  
    def getAnswersForAndGroupedBy(self, question_id, group_by):
        retval = {}
        question_row = self.getAnswerRow(question_id)
        #Strange, complex queries are waaay to slow
        country_row_id = self._query("select id from questions where question_field = \'%(country_row)s\'" % {'country_row' : self.country_row})[0][0]
        
        country_names = {}
        for text, id in self._query("select answer_text, answer_bit from answer_meanings where question_id = %(question_id)s", question_id = country_row_id):
            country_names[id] = text
        
        
        total_answers_per_country = []
        for id, count in self._query("select r.%(country_row)s, sum(r.est_wei2) from responses as r where %(question_row)s != 1 group by r.%(country_row)s" % \
            {'country_row' : self.country_row,
             'question_row' : question_row}):
            total_answers_per_country.append((country_names[id], count))
        
        
        discriminator_question_id = self._query("select id from questions where question_field = %(question)s", question = group_by)[0][0] 
        discriminator_answers = self._query("select answer_bit, answer_text from answer_meanings where question_id = %(question_id)s", question_id = discriminator_question_id)

        answer_map = self.connection.engine.execute('select show_which from questions where id = %(question_id)s', question_id=question_id).fetchall()[0][0]

        select_stmt = "%s" % group_by
        where_stmt = 'r.%s & %s = %s' % (question_row, answer_map, answer_map)
        group_by_stmt = "r.%s, r.%s" % (group_by, self.country_row)
        
        query_match = "select r.%(country_row)s, sum(r.est_wei2), r.%(select)s from responses as r WHERE %(where)s group by %(group_by)s" %\
          {'country_row' : self.country_row, 
           'select' : select_stmt,
           'where' : where_stmt,
           'group_by' : group_by_stmt}
        
        for (country_id, count, discriminator) in self._query(query_match):
            country = country_names[country_id]
            discriminators = retval.get(country, {})
            for(bit, name) in discriminator_answers:
                if(discriminator & bit):
                    discriminators[name] = discriminators.get(name, 0) + count
            retval[country] = discriminators
        
        for country, count in total_answers_per_country:
            discriminators = retval[country]
            for key in discriminators.keys():
                discriminators[key] = discriminators[key] / float(count)
                
        return retval
                                        
    def getAnswersForCountry(self, question_id, country, group_by = None):
        """
        Return a dictionary, key is the human readable answer and 
        the value another dictionary, key is the discriminator answer, and 
        value the percentage for this answer combination
        """
        if group_by in [None, '']:
            return self._innerGetAnswersForCountry(question_id, country)
        else:
            return self.getAnswersForCountryAndGroupedBy(question_id, country, group_by)

    def _innerGetAnswersForCountry(self, question_id, country):
        """
        Return a dictionary, key is the human readable answer and 
        the value another dictionary, key is the discriminator answer, and 
        value the percentage for this answer combination
        """
        question_row = self.getAnswerRow(question_id)
        map_answers = self._query("select answer_bit, answer_text from answer_meanings where question_id = %(question_id)s", question_id = question_id)

        total_answers_count = float(self._query("select sum(est_wei2) from responses where %s = %%(country)s and %s != 1" % (self.country_row, question_row), country = country)[0][0] or 0)

        retval = {}

        query_match = "select sum(est_wei2), %s from responses where %s = %%(country)s group by %s" % (question_row, self.country_row, question_row)
        
        for (count, answer_bit) in self._query(query_match, country = country):
            for bit, text in map_answers:
                if answer_bit & bit:
                    retval[text] = {"" : retval.get(text, {"":0})[""] + count}
                    
        for key in retval.keys():
            retval[key][""] = retval[key][""] / total_answers_count
            
        return retval
    
    def getAnswersForCountryAndGroupedBy(self, question_id, country, group_by):
        """
        Return a dictionary, key is the human readable answer and 
        the value another dictionary, key is the discriminator answer, and 
        value the percentage for this answer combination
        """
        retval = {}
        
        question_row = self.getAnswerRow(question_id)

        total_answers_count = float(self._query("select sum(est_wei2) from responses where %s != 1 and %s = %%(country)s" % (question_row, self.country_row), country = country)[0][0])

        discriminator_question_id = self._query("select id from questions where question_field = %(question)s", question = group_by)[0][0] 
        discriminator_answers = self._query("select answer_bit, answer_text from answer_meanings where question_id = %(question_id)s", question_id = discriminator_question_id)

        answer_map = {}
        
        for bit, text in self._query("select answer_bit, answer_text from answer_meanings where question_id = %(question_id)s", question_id = question_id):
            answer_map[text] = bit

        select_stmt = "%s" % group_by
        group_by_stmt = "%s, %s" % (question_row, group_by)
        query_match = "select %s, sum(est_wei2), %s from responses where %s = %%(country)s group by %s" % (question_row, select_stmt, self.country_row, group_by_stmt)
        
        for (current_answer_bit, count, discriminator) in self._query(query_match, country = country):
            for answer_text, answer_bit in answer_map.items():
                if not answer_bit & current_answer_bit:
                    continue
                if not retval.has_key(answer_text):
                    retval[answer_text] = {}
                discriminators = retval[answer_text]
                for(bit, name) in discriminator_answers:
                    if(discriminator & bit):
                        discriminators[name] = discriminators.get(name, 0) + count
        
        for discriminators in retval.values():
            for key in discriminators.keys():
                discriminators[key] = discriminators[key] / float(total_answers_count)
                
        return retval

    def getDiscriminators(self):
        return self._query('select question_field, question from questions where is_designator = 1')
            
        

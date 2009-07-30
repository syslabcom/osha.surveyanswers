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
    
    def __init__(self, context):
        self.context = context 
        self.db_name = context.getProperty('db_name')
        db_util = getUtility(IDatabase, self.db_name)
        connection = db_util.connection 
        meta = sa.MetaData()
        meta.bind = connection
        self.connection = connection
        self.responses = sa.Table('responses', meta, autoload=True)
        self.questions = sa.Table('questions', meta, autoload=True)
        self.answer_meanings = sa.Table('answer_meanings', meta, autoload=True)
        
    def _query(self, stmt, **kwargs):
        return self.connection.engine.execute(stmt, **kwargs).fetchall()
            
    def getAllQuestions(self):
        questionDicter = lambda x: {'name' : x[2], 'id': x[1]}
        all_questions = self.connection.execute(self.questions.select('')).fetchall()
        def reducer(retval, question):
            found = False
            for group in retval:
                if group['name'] == question[3]:
                    group['questions'].append(questionDicter(question))
                    found = True
            if not found:
                retval.append({'name' : question[3], 'questions': [questionDicter(question)]})
            return retval
        return reduce(reducer, all_questions, [])
            
    def hasQuestion(self, question):
        question_exists = self.connection.execute(self.questions.select('question_field=:question').params(question=question)).fetchall() 
        return question_exists
    
    def getAnswersFor(self, question):
        if not questionFilter(question):
            raise AttributeError("Warning invalid value supplied for question: %s" % question)
        map_answers = []
        for map_answer, type in self.connection.engine.execute('select map_answer, type from questions where question_field = :question', question=question).fetchall():
            map_answers.append(map_answer)
        where_stmt = ' or '.join(['%s & %s' % (question, x) for x in map_answers])
        yes = self._query('select question_1, count(*) from responses where %s group by question_1' % where_stmt) # save sql statement
        all = self._query('select question_1, count(*) from responses group by question_1')
        return dict(map(lambda ((country, yes), (i, all)): (country, float(yes) / all), zip(yes, all)))
         
    def getAnswersForCountry(self, question, country, group_by = None):
        if not questionFilter(question):
            raise AttributeError("Warning invalid value supplied for question: %s" % question)
        if not questionFilter(group_by):
            raise AttributeError("Warning invalid value supplied for group_by: %s" % question)
        question_id = self._query("select id from questions where question_field = :question", question = question)[0][0] 
        discriminator_question_id = self._query("select id from questions where question_field = :question", question = group_by)[0][0] 
        map_answers = self._query("select answer_bit, answer_text from answer_meanings where question_id = :question_id", question_id = question_id)
        discriminator_answers = self._query("select answer_bit, answer_text from answer_meanings where question_id = :question_id", question_id = discriminator_question_id)

        datasets = {}
        group_by_stmt = ""
        select_what_more = ""
        total_answers_count = float(self._query("select count(*) from responses where question_1 = :country", country = country)[0][0])
        if group_by:
            group_by_stmt = "group by %s" % group_by
            select_what_more = ", %s" % group_by

        for answer_bit, answer_text in map_answers:
            query_match = "select count(*) %s from responses where question_1 = :country and %s & %s %%s %s" % (select_what_more, question, answer_bit, group_by_stmt)
            answers_match = {}
            for (count, answer) in self._query(query_match % "", country = country):
                for discriminator_answer_bit, discriminator_answer_text in discriminator_answers:
                    discriminator_count = answers_match.get(discriminator_answer_text, 0)
                    if answer & discriminator_answer_bit:
                        discriminator_count += count
                        answers_match[discriminator_answer_text] = discriminator_count
            
            answers_match_percent = {}
            for key, value in answers_match.items():
                answers_match_percent[key] = "%02.2f" % (100 * value / total_answers_count)
            datasets[answer_text] = answers_match_percent
        return datasets
    
    
    def getDiscriminators(self):
        return self._query('select question_field, question from questions where designator = 1')
            
        
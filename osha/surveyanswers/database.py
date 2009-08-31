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
        self.db_name = context.getProperty('db_name')
        db_util = getUtility(IDatabase, self.db_name)
        connection = db_util.connection 
        meta = sa.MetaData()
        meta.bind = connection
        self.connection = connection
        self.responses = sa.Table('responses', meta, autoload=True)
        self.questions = sa.Table('questions', meta, autoload=True)
        self.map_data = sa.Table('map_data', meta, autoload=True)
        self.answer_meanings = sa.Table('answer_meanings', meta, autoload=True)
        
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
        all_questions = self.connection.execute(self.questions.select('')).fetchall()
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
        question_exists = self.connection.execute(self.questions.select('id=:question').params(question=question_id)).fetchall() 
        return question_exists
    
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
        retval = {}
        retval['rng1'] = question[2]
        retval['rng1_msg'] = question[3]
        retval['rng2'] = question[4]
        retval['rng2_msg'] = question[5]
        retval['rng3'] = question[6]
        retval['rng3_msg'] = question[7]
         
        return retval
    
    def getOrderedAnswerMeanings(self, question):
        question_id = self.getQuestionIdFromRowName(question)
        for country in self._query("select answer_text from answer_meanings where question_id = :question_id order by position", question_id = question_id):
            yield country[0]
            
    def getQuestionIdFromRowName(self, row_name):
        return self._query("select id from questions where question_field = :question_field", question_field = row_name)[0][0]
    

    def getAnswersFor(self, question_id):
        """
        Return a dictionary of relative percentages to show on map
        """
        answer_map = self.connection.engine.execute('select show_which from questions where id = :question_id', question_id=question_id).fetchall()[0][0]
        where_stmt = '%s & %s' % (self.getAnswerRow(question_id), answer_map)
        yes = self._query('select %(country_row)s, count(*) from responses where %(where)s group by %(country_row)s order by %(country_row)s' % ({'country_row' : self.country_row, 'where' : where_stmt})) # save sql statement
        all = self._query('select %(country_row)s, count(*) from responses group by %(country_row)s order by %(country_row)s' % {'country_row' : self.country_row})
        # Map and reduce in simple
        return dict(map(lambda ((country, yes), (i, all)): 
                            (country, 
                             (float(yes) / all)
                            ),
                         zip(yes, all)))
    
    def getAnswersForAndGroupedBy(self, question_id, group_by):
        if group_by and not questionFilter(group_by):
            raise AttributeError("Warning invalid value supplied for group_by: \"%s\"" % group_by)
        retval = {}

        total_answers_per_country = self._query("select a.answer_text, count(r.%(country_row)s) from responses as r, answer_meanings as a WHERE r.%(country_row)s == a.answer_bit and a.question_id == 0 group by r.%(country_row)s" % {'country_row' : self.country_row})
        
        discriminator_question_id = self._query("select id from questions where question_field = :question", question = group_by)[0][0] 
        discriminator_answers = self._query("select answer_bit, answer_text from answer_meanings where question_id = :question_id", question_id = discriminator_question_id)

        answer_map = self.connection.engine.execute('select show_which from questions where id = :question_id', question_id=question_id).fetchall()[0][0]

        select_stmt = "%s" % group_by
        where_stmt = 'r.%s & %s' % (self.getAnswerRow(question_id), answer_map)
        group_by_stmt = "r.%s, r.%s" % (group_by, self.country_row)
        
        query_match = "select a.answer_text, count(r.%s), r.%s from responses as r, answer_meanings as a WHERE r.%s == a.answer_bit and a.question_id == 0 and %s group by %s" %  (self.country_row, select_stmt, self.country_row, where_stmt, group_by_stmt)
        
        for (country, count, discriminator) in self._query(query_match):
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
        map_answers = self._query("select answer_bit, answer_text from answer_meanings where question_id = :question_id", question_id = question_id)

        total_answers_count = float(self._query("select count(*) from responses where %s = :country" % self.country_row, country = country)[0][0])

        retval = {}

        query_match = "select count(*), %s from responses where %s = :country group by %s" % (question_row, self.country_row, question_row)
        
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

        total_answers_count = float(self._query("select count(*) from responses where %s = :country" % self.country_row, country = country)[0][0])

        discriminator_question_id = self._query("select id from questions where question_field = :question", question = group_by)[0][0] 
        discriminator_answers = self._query("select answer_bit, answer_text from answer_meanings where question_id = :question_id", question_id = discriminator_question_id)

        answer_map = {}
        
        for bit, text in self._query("select answer_bit, answer_text from answer_meanings where question_id = :question_id", question_id = question_id):
            answer_map[text] = bit

        select_stmt = "%s" % group_by
        question_row = self.getAnswerRow(question_id)
        group_by_stmt = "%s, %s" % (question_row, group_by)
        query_match = "select %s, count(*), %s from responses where %s = :country group by %s" % (question_row, select_stmt, self.country_row, group_by_stmt)
        
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
            
        

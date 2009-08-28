from zope.interface import Interface
from plone.portlets.interfaces import IPortletDataProvider

class ISingleQuestion(Interface):
    pass

class ISurvey(Interface):
    pass

class ISurveyDatabase(Interface):
    def getAllQuestions(self):
        """
        Return a list of tuples with question and question key
        """
        
    def getAnswersFor(self, question):
        """
        Return all answers for the given question
        """
        
    def hasQuestion(self, question):
        """
        Return whether the question exists
        """
        
class IQuestionsPortlet(IPortletDataProvider):
    pass
from zope import interface
from zope.app.content import interfaces as contentifaces

class IAnswers(interface.Interface):
    """ An abstract interface common to all answers, for the first map view"""
    
class IYesNoAnswers(IAnswers):
    """ A subtype for documents representing a yes no answer"""

class ISingleChoiceUnorderedAnswers(IAnswers):
    """ A subtype for documents representing a single choice question"""
    
class ISingleChoiceOrderedAnswers(IAnswers):
    """ A subtype for documents representing a single choice question.
        Answers to this questions can be summed"""

interface.alsoProvides(IYesNoAnswers, contentifaces.IContentType)
interface.alsoProvides(ISingleChoiceUnorderedAnswers, contentifaces.IContentType)
interface.alsoProvides(ISingleChoiceOrderedAnswers, contentifaces.IContentType)

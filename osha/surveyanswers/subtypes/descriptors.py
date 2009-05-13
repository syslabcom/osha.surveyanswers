from osha.surveyanswers.subtypes.interfaces import IYesNoAnswers, \
    ISingleChoiceUnorderedAnswers, ISingleChoiceOrderedAnswers
from p4a.subtyper.interfaces import IPortalTypedDescriptor
from zope import interface

class YesNoAnswersDescriptor(object):
    interface.implements(IPortalTypedDescriptor)
    title = u'Yes No Answers'
    description = u'Represents the answers to a question that can only'\
                  u'be answered with yes or no'
    type_interface = IYesNoAnswers
    for_portal_type = 'File'

class SingleChoiceUnorderedAnswersDescriptor(object):
    interface.implements(IPortalTypedDescriptor)
    title = u'Single choice unordered answers'
    description = u'Represents the answers to a question that can be'\
                  u'be answered by choosing one of many options'\
                  u'The options are unordered and unrelated to the next'
    type_interface = ISingleChoiceUnorderedAnswers
    for_portal_type = 'File'

class SingleChoiceOrderedAnswersDescriptor(object):
    interface.implements(IPortalTypedDescriptor)
    title = u'Single choice ordered answers'
    description = u'Represents the answers to a question that can be'\
                  u'be answered by choosing one of many options'\
                  u'The options are ordered. If somebody chose option 2,'\
                  u'he also chose all options above, 3, 4, 5...'
    type_interface = ISingleChoiceOrderedAnswers
    for_portal_type = 'File'

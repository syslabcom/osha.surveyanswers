from Acquisition import aq_inner #@UnresolvedImport
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter #@UnresolvedImport
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base

from osha.surveyanswers import OshaMessageFactory as _
from osha.surveyanswers.interfaces import IQuestionsPortlet, ISurveyDatabase

class Assignment(base.Assignment):
    implements(IQuestionsPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        return _(u"Questions")

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('portletquestions.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()

        # save the question id of the current question
        # Due to apache rewriting, we cannot use PATH_INFO, but must contruct the path manually
        # first, get the URL and snip the SERVER_URL off
        path = self.request.get('URL')[len(self.request.get('SERVER_URL'))+1:]
        # then pre-pend VirtualURL components if present
        elems = [x for x in self.request.get('VirtualRootPhysicalPath', [''])] + path.split('/')
        # The question id is the last or last-but-one element
        selected_question_id = elems[len(context.getPhysicalPath())-len(elems)]
        try:
            self.selected_question_id = int(selected_question_id)
        except ValueError:
            self.selected_question_id = ''

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()
        self.db = ISurveyDatabase(self.context)

    @property
    def all_questions(self):
        self.context.getCanonicalLanguage()
        for questions in self.db.getAllQuestions():
            if questions['name'] not in ['Gruppe', 'Discriminator question']:
                questions['count'] = len(questions['questions'])
                questions['selected'] = 0
                for question in questions['questions']:
                    if question['question_id'] == self.selected_question_id:
                        question['selected'] = 1
                        questions['selected'] = 1
                    else:
                        question['selected'] = 0
                    question['text'] = _(question['text'])
                questions['name'] = _(questions['name'])
                yield questions

    def render(self):
        return self._template()

    @property
    def available(self):
        return True

class AddForm(base.AddForm):
    form_fields = form.Fields(IQuestionsPortlet)
    label = _(u"Add Questions Portlet")
    description = _(u"This portlet displays all questions.")

    def create(self, data):
        return Assignment()

class EditForm(base.EditForm):
    form_fields = form.Fields(IQuestionsPortlet)
    label = _(u"Edit Questions Portlet")
    description = _(u"This portlet displays all questions.")

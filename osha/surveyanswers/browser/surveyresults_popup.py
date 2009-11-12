import Acquisition
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class ResultsPopoupView(BrowserView):
    """ View for displaying (ESENER) survey results inside a popup
    """
    template = ViewPageTemplateFile('surveyresults_popup.pt')
    template.id = "surveyresults_popup"

    def __call__(self):
        self.request.set('disable_border', True)

        return self.template() 
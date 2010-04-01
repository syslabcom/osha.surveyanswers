from osha.theme.browser.viewlets import OSHALanguageSelector
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.i18n.locales.browser.selector import LanguageSelector
from zope.component import getMultiAdapter
from Products.LinguaPlone.interfaces import ITranslatable

class ESENERLanguageSelector(OSHALanguageSelector):
    """ Override LinguaPlone's language selector to provide our own template
        This is used for content that is LinguaPlone translatable """

    _template = ViewPageTemplateFile('languageselector.pt')

    def languages(self):
        results = LanguageSelector.languages(self)
        
        # On the main portal, we want to be able to filter out unwanted
        # languages needes for subsites
        oshaview = getMultiAdapter((self.context, self.request), name='oshaview')
        subsite_path = oshaview.subsiteRootPath()
        potential_subsite = self.context.restrictedTraverse(subsite_path)
            
        # get the potentially present question- and country-id
        # Due to apache rewriting, we cannot use PATH_INFO, but must contruct the path manually
        # first, get the URL and snip the SERVER_URL off
        path = self.request.get('URL')[len(self.request.get('SERVER_URL'))+1:]
        # then pre-pend VirtualURL components if present
        elems = [x for x in self.request.get('VirtualRootPhysicalPath', [''])] + path.split('/')
        # join it to a path
        virtual_path = '/'.join(elems)
        # get the context's path
        context_path = '/'.join(self.context.getPhysicalPath())
        # just an extra test, as the following expression should always be true
        if virtual_path.startswith(context_path):
            question_path = virtual_path[len(context_path):]
        else:
            question_path = ''

        group_by = 'group_by' in self.request and '&group_by=' + \
            self.request.get('group_by') or ''

        # for translatable content, directly link to the translated objects
        translatable = ITranslatable(self.context, None)
        if translatable is not None:
            translations = translatable.getTranslations()
        else:
            translations = []

        for data in results:
            data['translated'] = data['code'] in translations
            if data['translated']:
                trans = translations[data['code']][0]
                state = getMultiAdapter((trans, self.request),
                        name='plone_context_state')
                data['url'] = state.view_url() + question_path + \
                    '?set_language=' + data['code'] + group_by
            else:
                state = getMultiAdapter((self.context, self.request),
                        name='plone_context_state')
                try:
                    data['url'] = state.view_url() + '/not_available_lang?set_language=' + data['code']
                except AttributeError:
                    data['url'] = self.context.absolute_url() + '/not_available_lang?set_language=' + data['code']

        return results

from osha.theme.browser.viewlets import OSHALanguageSelector
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

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
            

        for data in results:
            data['url'] = self.context.absolute_url()+'/switchLanguage?set_language='+data['code']
        return results

        # for translatable content, directly link to the translated objects
        translatable = ITranslatable(self.context, None)
        if translatable is not None:
            translations = translatable.getTranslations()
        else:
            translations = []
        links =  self.context.getBRefs('lingualink')
        # create a dict that maps language to LinguaLink object
        lang_to_link = dict()
        for link in links:
            lang_to_link[link.Language()] = link

        for data in results:
            data['translated'] = data['code'] in translations
            if data['translated']:
                trans = translations[data['code']][0]
                state = getMultiAdapter((trans, self.request),
                        name='plone_context_state')
                data['url'] = state.view_url() + '?set_language=' + data['code']
            elif data['code'] in lang_to_link:
                data['url'] = lang_to_link[data['code']].absolute_url()
            else:
                state = getMultiAdapter((self.context, self.request),
                        name='plone_context_state')
                try:
                    data['url'] = state.view_url() + '/not_available_lang?set_language=' + data['code']
                except AttributeError:
                    data['url'] = self.context.absolute_url() + '/not_available_lang?set_language=' + data['code']

        return results

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2


class OshaSurveyAnswers(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import osha.surveyanswers
        self.loadZCML('configure.zcml', package=osha.surveyanswers)

        z2.installProduct(app, 'osha.surveyanswers')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'osha.surveyanswers:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'osha.surveyanswers')


OSHA_SURVEYANSWERS_FIXTURE = OshaSurveyAnswers()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(OSHA_SURVEYANSWERS_FIXTURE,),
    name="OshaSurveyAnswers:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OSHA_SURVEYANSWERS_FIXTURE,),
    name="OshaSurveyAnswers:Functional")

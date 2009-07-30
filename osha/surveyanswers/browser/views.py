from osha.surveyanswers.parsers import SHORT_NAME_TO_ID, country_extractor
from Products.Five.browser import BrowserView
from zope.component import getUtility #@UnresolvedImport
from collective.lead.interfaces import IDatabase
import sqlalchemy as sa #@UnresolvedImport
from zope.component import adapts #@UnresolvedImport
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPublisher,\
    IBrowserView
from Products.ATContentTypes.interface.document import IATDocument
from osha.surveyanswers.interfaces import ISurvey, ISingleQuestion,\
    ISurveyDatabase
from ZPublisher.BaseRequest import DefaultPublishTraverse
from zope.component import getMultiAdapter #@UnresolvedImport

class SurveyTraverser(object):
    implements(IBrowserPublisher)
    adapts(ISurvey, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def publishTraverse(self, request, name):
        if name == 'document_view':
            return getMultiAdapter((self.context, self.request), name=name).__of__(self.context)
        db = ISurveyDatabase(self.context)
        if db.hasQuestion(name):
            view = getMultiAdapter((self.context, self.request), name="question").__of__(self.context)
            view.init(name)
            return view
        return DefaultPublishTraverse(self.context, self.request).publishTraverse(self.request, name)
    
    def browserDefault(self, request):
        return QuestionOverView(self.context, self.request), tuple()
    
class CountryTraverser(object):
    implements(IBrowserPublisher)
    adapts(ISingleQuestion, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def publishTraverse(self, request, name):
        db = ISurveyDatabase(self.context.context)
        if db.hasQuestion(self.context.question):
            view = getMultiAdapter((self.context.context, self.request), name="question_country").__of__(self.context.context)
            view.init(self.context.question, name)
            return view
        return DefaultPublishTraverse(self.context.context, self.request).publishTraverse(self.request, name)
    
    def browserDefault(self, request):
        return self.context, tuple()

class SingleQuestionCountry(object):
    implements(IBrowserView)
    adapts(ISurvey, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.db = ISurveyDatabase(self.context)

    def init(self, name, country):
        self.question = name
        self.country = country

    def absolute_url(self):
        return self.context.context.absolute_url()
    
    @property
    def discriminators(self):
        return [{"key" : x[0], "value" : x[1]} for x in self.db.getDiscriminators()]
        
class QuestionOverView(BrowserView):
    implements(IBrowserView)
    adapts(ISurvey, IBrowserRequest)
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.db = ISurveyDatabase(self.context)
        
    @property
    def all_questions(self):
        return self.db.getAllQuestions()
    
class SingleQuestion(object):
    implements(IBrowserView, ISingleQuestion)
    adapts(ISurvey, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.db = ISurveyDatabase(self.context)
        
    def init(self, name):
        self.question = name
        
    @property
    def countries(self):
        return ['chartdiv-' + id for id in SHORT_NAME_TO_ID.values()]

    def absolute_url(self):
        return self.context.context.absolute_url()
        
class FusionJS(object):
    
    default_params = dict(border_color='005879'
                  , fill_color='D7F4FF'
                  , number_suffix=' % '
                  , label_sep_char=': '
                  , base_font_size='9'
                  , map_name='FCMap_Europe.swf'
    )
    
    static_xml = """
function drilldown(chart){
  var chart_to_show = jq('#chartdiv-' + chart)
  if (chart_to_show){
      chart_to_show.show();
    jq('#drilled_down_button').show();
    jq('.not_drilled_down').hide();
  }
}
function drillback(){
  jq('.drilled_down').hide();
  jq('.not_drilled_down').show();
}
// Stupid trick to get around a problem. If the flash map is not completely
// rendered yet, the html that contains links will be added in a way
// that firefox interprets it wrongly
function FC_Rendered(DOMId){
  fmap.setDataXML(xmlMapData);
  jq('#mapdiv').show();  
   }

"""


    xml_map_template = """
    <map borderColor='%(border_color)s' 
         fillColor='%(fill_color)s' 
         animation='0'
         includeNameInLabels='0' 
         numberSuffix='%(number_suffix)s' 
         includeValueInLabels='1' 
         labelSepChar='%(label_sep_char)s' 
         baseFontSize='%(base_font_size)s'>
      <data>%(contents)s</data>
    </map>
    """.replace("\n", "")
    xml_chart_template = """var xmlChartData = "
    <chart  
           numberSuffix= '%%'>
      <categories>
        %s
      </categories>
        %s
</chart>";
""".replace("\n", "")   
              
    
    extractors = {}

    def __call__(self):
        retval = []
        self.question = self.request.form['question']
        self.country = self.request.form.get('country', '')
        self.group_by = self.request.form.get('group_by', '')
        if self.group_by == 'None':
            self.group_by = ''
        retval.append(self.static_xml)
        retval.append(self.contents())
        retval.append(self.flash_init())
        
        return "\n".join(retval)

    def contents(self):
        db = ISurveyDatabase(self.context)
        if not self.country:
            contents = db.getAnswersFor(self.question)
            map_contents = ''.join(country_extractor('/'.join((self.context.absolute_url(), self.question)), contents))
        
            map_data_full = "var xmlMapData = \"%s\";" % self.getMapData(map_contents)
            map_data_empty = "var xmlMapDataEmpty = \"%s\";" % self.getMapData()
            datasets = []
            values_xml = []
            for value in contents.values():
                values_xml.append("<set value='%s' />" % value)
            datasets.append("<dataset seriesName=''>%s\</dataset>" % ("".join(values_xml)))
            categories = ["<category label='' />"]
            charts_data = self.xml_chart_template % ("".join(categories), "".join(datasets))
            return "\n".join([map_data_full, map_data_empty, charts_data])
        else:
            contents = db.getAnswersForCountry(self.question, self.country, self.group_by)
            charts_data = []
            datasets = []
            for key, values in contents.items():
                values_xml = "".join(["<set value='%s' />" % value for value in values.values()])
                datasets.append("<dataset seriesName='%s'>%s\</dataset>" % (key, values_xml))
            categories = []
            for key in contents.values()[0].keys():
                categories.append("<category label='%s' />" % key)
            charts_data = self.xml_chart_template % ("".join(categories), "".join(datasets))
            return charts_data
    
    def flash_init(self):
        if not self.country:
            fusion_map = """
            var fmap = new FusionMaps("%s", "Map1Id", "750", "400", "0", "1");
            fmap.setDataXML(xmlMapDataEmpty);
            fmap.render("mapdiv");
            """ % self.getMapParams()['map_name'] 
            chart_map = """
            var myChart = new FusionCharts("MSColumn2D.swf", "myChartId", "900", "300", "0", "1");
            alert(xmlChartData);
            myChart.setDataXML(xmlChartData);
            myChart.render("chartdiv");
            """
            retval = fusion_map + chart_map
        else:
            chart_map = """
            var myChart = new FusionCharts("MSColumn2D.swf", "myChartId", "900", "300", "0", "1");
            myChart.setDataXML(%s);
            myChart.render("chartdiv");
            """
            retval = chart_map % ('xmlChartData')
        return retval

    def getMapData(self, contents=''):
        params = self.getMapParams()
        params['contents'] = contents
        return self.xml_map_template % params
    
    def getMapParams(self):
        """
        Generate a parameter map from the default parameters, or
        the parameters set in zope
        """
        params = {}
        param_setter = lambda params, x: params.__setitem__(x, self.default_params.get(x))
        for key in self.default_params:
            param_setter(params, key)
        return params

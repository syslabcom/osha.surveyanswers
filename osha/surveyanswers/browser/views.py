from Products.Five.browser import BrowserView
from zope.component import adapts #@UnresolvedImport
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPublisher,\
    IBrowserView
from osha.surveyanswers.interfaces import ISurvey, ISingleQuestion,\
    ISurveyDatabase
from ZPublisher.BaseRequest import DefaultPublishTraverse
from zope.component import getMultiAdapter #@UnresolvedImport
from osha.surveyanswers.constants import ID_TO_SHORT_NAME, SHORT_NAME_TO_ID,\
    SHORT_NAME_TO_LONG, ID_TO_LONG_NAME

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
        if db.hasQuestion(self.context.question_id):
            view = getMultiAdapter((self.context.context, self.request), name="question_country").__of__(self.context.context)
            view.init(self.context.question_id, name)
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

    def init(self, question_id, country):
        self.question_id = question_id
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
        for questions in self.db.getAllQuestions():
            if questions['name'] not in ['Gruppe', 'Discriminator question']:
                questions['count'] = len(questions['questions'])
                yield questions
    
class SingleQuestion(object):
    implements(IBrowserView, ISingleQuestion)
    adapts(ISurvey, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.db = ISurveyDatabase(self.context)
        
    def init(self, question_id):
        self.question_id = question_id
        
    @property
    def question_text(self):
        return self.db.getQuestion(self.question_id)['text']
    
    @property
    def countries(self):
        return ['chartdiv-' + id for id in SHORT_NAME_TO_ID.values()]
    
    @property
    def discriminators(self):
        return [{"key" : x[0], "value" : x[1]} for x in 
                [x for x in self.db.getDiscriminators() if x[0] in ['question_2', 'question_3']]]

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
         showCanvasBorder='0'
         showLegend='1'
         includeNameInLabels='0' 
         numberSuffix='%(number_suffix)s' 
         includeValueInLabels='1' 
         labelSepChar='%(label_sep_char)s' 
         baseFontSize='%(base_font_size)s'>
            <colorRange>
        <color minValue='0' maxValue='%(rng1)i' displayValue='%(rng1_msg)s' color='A7E9BC' />
        <color minValue='%(rng1)i' maxValue='%(rng2)i' displayValue='%(rng2_msg)s' color='FFFFCC' />
        <color minValue='%(rng2)i' maxValue='100' displayValue='%(rng3_msg)s' color='FF9377' />
   </colorRange>
      <data>%(contents)s</data>
    </map>
    """.replace("\n", "")
    xml_chart_template = """var xmlChartData = "
    <chart  
           numberSuffix= '%%'
           labelDisplay='ROTATE'>
      <categories>
        %s
      </categories>
        %s
</chart>";
""".replace("\n", "")   
              
    
    extractors = {}
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.db = ISurveyDatabase(self.context)

    def __call__(self):
        retval = []
        self.question_id = self.request.form['question_id']
        self.country = self.request.form.get('country', '')
        self.group_by = self.request.form.get('group_by', '')
        if self.group_by == 'None':
            self.group_by = ''
        retval.append(self.static_xml)
        retval.append(self.contents())
        retval.append(self.flash_init())
        
        return "\n".join(retval)

    def contents(self):
        if not self.country:
            contents = self.db.getAnswersFor(self.question_id)

            SINGLE_DATASET = "<entity id = '%(shortname)s' value = '%(value)s' link='%(question)s/%(shortname)s' /\" + \">"
            def country_extractor(context, results): 
                for key, value in SHORT_NAME_TO_ID.items():
                    yield (SINGLE_DATASET % ({'shortname' : SHORT_NAME_TO_ID.get(key, ''), 
                                  'value' : "%02.2f" % (results.get(int(value), 0) * 100),
                                  'question' : context}))
                    
            map_contents = ''.join(country_extractor('/'.join((self.context.absolute_url(), self.question_id)), contents))
                
            map_data_full = "var xmlMapData = \"%s\";" % self.getXMLMapData(map_contents)
            map_data_empty = "var xmlMapDataEmpty = \"%s\";" % self.getXMLMapData()
            
            
            if self.group_by:
                chart_contents = self.db.getAnswersForAndGroupedBy(self.question_id, self.group_by)
            else:
                keyToName = lambda x: ID_TO_LONG_NAME['%03i' % (x + 1)]
                inner = {}
                for key, value in contents.items():
                    inner[keyToName(key)] = value
                chart_contents = {'':inner}
                
            charts_data = self.getXMLChartData(chart_contents)
            return "\n".join([map_data_full, map_data_empty, charts_data])
        else:
            chart_contents = self.db.getAnswersForCountry(self.question_id, self.country, self.group_by)
            return self.getXMLChartData(chart_contents)
        
    def flash_init(self):
        if not self.country:
            fusion_map = """
            var fmap = new FusionMaps("%s", "Map1Id", "750", "400", "0", "1");
            fmap.setDataXML(xmlMapDataEmpty);
            fmap.render("mapdiv");
            """ % self.getMapParams()['map_name'] 
            chart_map = """
            var myChart = new FusionCharts("MSColumn2D.swf", "myChartId", "900", "300", "0", "1");
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

    def getXMLMapData(self, contents=''):
        params = self.getMapParams()
        map_info = self.db.getMapInfo(self.question_id)
        params.update(map_info)
        params['contents'] = contents
        return self.xml_map_template % params
    
    def getXMLChartData(self, chart_contents):
        categories = ["<category label='%s' />" % x for x in chart_contents.values()[0].keys()]
        datasets = []
        for key, values in chart_contents.items():
            values_xml = "".join(["<set value='%02.2f' />" % (value * 100) for value in values.values()])
            datasets.append("<dataset showValues='0' seriesName='%s'>%s\</dataset>" % (key, values_xml))
        return self.xml_chart_template % ("".join(categories), "".join(datasets))
            
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
    
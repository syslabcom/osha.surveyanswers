from xml.sax.saxutils import escape
import StringIO

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import adapts, getMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPublisher,\
    IBrowserView
from ZPublisher.BaseRequest import DefaultPublishTraverse

import xlwt

from osha.surveyanswers import OshaMessageFactory as _

from osha.surveyanswers.constants import ID_TO_SHORT_NAME, SHORT_NAME_TO_ID,\
    SHORT_NAME_TO_LONG, ID_TO_LONG_NAME, LONG_TO_TRANSLATED
from osha.surveyanswers.interfaces import ISurvey, ISingleQuestion,\
    ISurveyDatabase

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
        self.translate = lambda x:\
            getToolByName(self.context, 'translation_service').\
            translate(x, context=self.context)

    def init(self, question_id, country):
        self.question_id = question_id
        self.country = country

    def absolute_url(self):
        return self.context.context.absolute_url()
    
    @property
    def question_text(self):
        return _(self.db.getQuestion(self.question_id)['text'])

    @property
    def country_name(self):
        return LONG_TO_TRANSLATED[ID_TO_LONG_NAME[self.country]]
    
    @property
    def discriminators(self):
        return [{"key" : x[0], "value" : self.translate(_(x[1]))} for x in self.db.getDiscriminators()]
        
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

class XLSDownload(object):
    implements(IBrowserView)
    adapts(ISurvey, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.db = ISurveyDatabase(self.context)
        self.translate = lambda x:\
            getToolByName(self.context, 'translation_service').\
            translate(x, context=self.context)

    def __call__(self, question, country = "", group_by = ""):
        if group_by == 'None':
            group_by = ''
        wb = xlwt.Workbook()
        ws = wb.add_sheet(' ')
        datasets = [[self.db.getQuestion(question)['text']]]
        if not country:
            if group_by:
                data = self.db.getAnswersForAndGroupedBy(question, group_by)
                headers = data.values()[0].keys()
                headers.sort()
                datasets.append(["All values refer to the answer %s" % self.db.getMapInfo(question)['show_which_answer']])
                datasets.append([""] + headers)
                countries = data.keys()
                countries.sort()
                for country in countries:
                    values = data[country]
                    datasets.append([country] + [values[x] for x in headers])
            else:
                data = self.db.getAnswersFor(question)
                datasets.append(['Country',_(self.db.getMapInfo(question)['show_which_answer'])])
                tmp_keys = data.keys()
                for key in tmp_keys:
                    data[self.translate(LONG_TO_TRANSLATED[ID_TO_LONG_NAME['%03i' % key]])] = data.pop(key)
                countries = data.keys()
                countries.sort()
                for country in countries:
                    datasets.append([country, data[country]])
            #datasets.extend([x for x in self.db.getAnswersForExport(question)])
        else:
            datasets.append(["Country: " + self.db.getCountryName(country)])
            if group_by:
                group_by_description = self.db.getQuestion(self.db.getQuestionIdFromRowName(group_by))['text']
                group_by_row_names = self.db.getOrderedAnswerMeanings(group_by)
            else:
                group_by = ""
                group_by_description = ""
                group_by_row_names = [""]
            raw_datasets = self.db.getAnswersForCountry(question, country, group_by)
            row_head = [x for x in self.db.getOrderedAnswerMeanings(self.db.getAnswerRow(question))]
            datasets.append([group_by_description] + row_head)
            for row_key in group_by_row_names:
                row = [row_key]
                datasets.append(row)
                for cell_key in row_head:
                    row.append(raw_datasets.get(cell_key, {}).get(row_key, 0))
        for row in range(len(datasets)):
            row_data = datasets[row]
            for cell in range(len(row_data)):
                ws.write(row, cell, type(row_data[cell]) == float and "%02.2f %%" % ( 100 * row_data[cell]) or row_data[cell])
        retval = StringIO.StringIO()
        wb.save(retval)
        self.request.RESPONSE.setHeader("Content-type","application/vnd.ms-excel")
        self.request.RESPONSE.setHeader("Content-disposition","attachment;filename=statistics.xls")
        return retval.getvalue()
    
class SingleQuestion(object):
    implements(IBrowserView, ISingleQuestion)
    adapts(ISurvey, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.db = ISurveyDatabase(self.context)
        self.translate = lambda x:\
            getToolByName(self.context, 'translation_service').\
            translate(x, context=self.context)
        
    def init(self, question_id):
        self.question_id = question_id
        
    @property
    def question_text(self):
        return _(self.db.getQuestion(self.question_id)['text'])
    
    @property
    def countries(self):
        return ['chartdiv-' + id for id in SHORT_NAME_TO_ID.values()]
    
    @property
    def discriminators(self):
        return [{"key" : x[0], "value" : self.translate(_(x[1]))} for x in 
                [x for x in self.db.getDiscriminators() if x[0] in ['sec3', 'size_5']]]

    def absolute_url(self):
        return self.context.context.absolute_url()
        
class FusionJS(object):
    
    default_params = dict(border_color='005879'
                  , fill_color='ffffff'
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
         connectorAlpha='0'
         connectorColor='0'
         animation='0'
         showCanvasBorder='0'
         showLegend='1'
         legendCaption='%(show_which_answer)s'
         includeNameInLabels='0' 
         numberSuffix='%(number_suffix)s' 
         includeValueInLabels='0' 
         labelSepChar='%(label_sep_char)s' 
         baseFontSize='%(base_font_size)s'>
            <colorRange>
        <color minValue='0' maxValue='%(rng1)i' displayValue='%(rng1_msg)s' color='CFCFCF' />
        <color minValue='%(rng1)i' maxValue='%(rng2)i' displayValue='%(rng2_msg)s' color='A8B1C2' />
        <color minValue='%(rng2)i' maxValue='100' displayValue='%(rng3_msg)s' color='7681A2' />
   </colorRange>
      <data>%(contents)s</data>
    </map>
    """.replace("\n", "")
    xml_chart_template = """var xmlChartData = "
    <chart
           showBorder='0'
           bgColor='ffffff'
           showExportDataMenuItem='1'
           yAxisMaxValue='100'
           numberSuffix= '%%'
           labelDisplay='ROTATE'
           staggerLines='3'>
      <categories>
        %s
      </categories>
        %s
</chart>";
""".replace("\n", "")

    xml_detail_template = """var xmlChartData = "
    <chart
           showBorder='0'
           bgColor='ffffff'
           showExportDataMenuItem='1'
           yAxisMaxValue='100'
           numberSuffix= '%%'
           labelDisplay='STAGGER'
           staggerLines='2'>
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
        self.translate = lambda x:\
            getToolByName(self.context, 'translation_service').\
            translate(x, context=self.context)

    def __call__(self):
        self.request.RESPONSE.setHeader('Cache-control', 'max-age=32140800')
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

            SINGLE_DATASET = "<entity id = '%(shortid)s' displayValue='%(shortname)s' value = '%(value)s' link='%(question)s/%(shortid)s' /\" + \">"
            def country_extractor(context, results):
                all_countries = SHORT_NAME_TO_ID.items()
                for key, value in all_countries:
                    if results.get(int(value), None) == None:
                        continue
                    yield (SINGLE_DATASET % (\
                    {'shortname' :key,
                     'shortid' : SHORT_NAME_TO_ID.get(key, ''), 
                     'value' : "%02.2f" % (results.get(int(value), 0) * 100),
                     'question' : context}))
                    
            map_contents = ''.join(country_extractor('/'.join((self.context.absolute_url(), self.question_id)), contents))
                
            map_data_full = "var xmlMapData = \"%s\";" % self.getXMLMapData(map_contents)
            map_data_empty = "var xmlMapDataEmpty = \"%s\";" % self.getXMLMapData()
            
            
            if self.group_by:
                chart_contents = self.db.getAnswersForAndGroupedBy(self.question_id, self.group_by)
                sorted_keys_dataset = self.db.getOrderedAnswerMeanings(self.group_by)
            else:
                sorted_keys_dataset = [""]
                keyToName = lambda x: self.translate(ID_TO_LONG_NAME['%03i' % (x)])
                chart_contents = {}
                for key, value in contents.items():
                    chart_contents[keyToName(key)] = {"": value}
                
            sorted_keys_category = self.db.getOrderedAnswerMeanings(self.db.country_row)
            # sort countries by their abbreviation
            sorted_keys_category = [x for x in sorted_keys_category]
            sorted_keys_category.sort(lambda x,y: cmp(
                LONG_TO_TRANSLATED.get(x,x), LONG_TO_TRANSLATED.get(y,y)))
                
            charts_data = self.getXMLChartData(chart_contents, sorted_keys_category, sorted_keys_dataset)
            return "\n".join([map_data_full, map_data_empty, charts_data])
        # We are on a country
        else:
            if self.group_by:
                sorted_keys_dataset = self.db.getOrderedAnswerMeanings(self.group_by)
            else:
                sorted_keys_dataset = [""]
            
            
            sorted_keys_category = self.db.getOrderedAnswerMeanings(self.db.getAnswerRow(self.question_id))
            chart_contents = self.db.getAnswersForCountry(self.question_id, self.country, self.group_by)
            return self.getXMLDetailData(chart_contents, sorted_keys_category, sorted_keys_dataset)
        
    def flash_init(self):
        if not self.country:
            fusion_map = """
            fmap = new FusionMaps("%s", "Map1Id", "500", "400", "0", "1");
            fmap.render("mapdiv");
            fmap.setDataXML(xmlMapDataEmpty);
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
        for key in ['show_which_answer', 'rng1_msg', 'rng2_msg', 'rng3_msg']:
            params[key] = self.translate(_(params[key]))
        return self.xml_map_template % params
    
    def getXMLChartData(self, chart_contents, sorted_categories, sorted_dataset):
        sorted_categories_non_empty = [x for x in sorted_categories if x in chart_contents.keys()]
        categories = ["<category label='%s' />" % LONG_TO_TRANSLATED.get(x, x) for x in sorted_categories_non_empty]
        datasets = []
        for key in sorted_dataset:
            values = [chart_contents[x].get(key, 0) for x in sorted_categories_non_empty]
            values_xml = "".join(["<set value='%02.2f' />" % (value * 100) for value in values])
            datasets.append("<dataset showValues='0' seriesName='%s'>%s\</dataset>" % (self.translate(_(key)), values_xml))
        return self.xml_chart_template % ("".join(categories), "".join(datasets))

    def getXMLDetailData(self, chart_contents, sorted_categories, sorted_dataset):
        sorted_categories_non_empty = [x for x in sorted_categories if x in chart_contents.keys()]
        categories = ["<category label='%s' />" % self.translate(_(x)) for x in sorted_categories_non_empty]
        datasets = []
        for key in sorted_dataset:
            values = [chart_contents[x].get(key, 0) for x in sorted_categories_non_empty]
            values_xml = "".join(["<set value='%02.2f' />" % (value * 100) for value in values])
            datasets.append("<dataset showValues='0' seriesName='%s'>%s\</dataset>" % (self.translate(_(key)), values_xml))
        return self.xml_detail_template % ("".join(categories), "".join(datasets))
            
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
    

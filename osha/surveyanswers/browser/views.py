from osha.surveyanswers.parsers import SHORT_NAME_TO_ID, extractor
class FusionMap(object):
    '''
    A View on Folders to be used for fusion maps
    '''
    @property
    def countries(self):
        return ['chartdiv-' + id for id in SHORT_NAME_TO_ID.values()]
    
    
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
           numberSuffix= '%'>
      <categories>
        <category label='Male' />
        <category label='Female' />
        <category label='Both' />
      </categories>
      <dataset seriesName='yes'>
        <set value='40' />
        <set value='20' />
        <set value='30' />
      </dataset>
      <dataset seriesName='no'>
        <set value='20' />
        <set value='60' />
        <set value='40' />
      </dataset>
      <dataset seriesName='NA'>
        <set value='40' />
        <set value='20' />
        <set value='30' />
      </dataset>
</chart>";
""".replace("\n", "")   
              
    
    extractors = {}

    def __call__(self):
        retval = []
        retval.append(self.static_xml)
        retval.append(self.contents())
        retval.append(self.flash_init())
        
        return "\n".join(retval)

    def contents(self):
        map_contents = ''.join(extractor(str(self.context)))
        
        map_data_full = "var xmlMapData = \"%s\";" % self.getMapData(map_contents)
        map_data_empty = "var xmlMapDataEmpty = \"%s\";" % self.getMapData()
        charts_data = [self.xml_chart_template]
        
        return "\n".join(charts_data + [map_data_full, map_data_empty])
    
    def flash_init(self):
        fusion_map = """
        var fmap = new FusionMaps("++resource++surveyanswers_flash/%s", "Map1Id", "750", "400", "0", "1");
        fmap.setDataXML(xmlMapDataEmpty);
        fmap.render("mapdiv");
        """ % self.getMapParams()['map_name'] 
        chart_map = """
        var myChart = new FusionCharts("++resource++surveyanswers_flash/MSColumn2D.swf", "myChartId", "900", "300", "0", "1");
        myChart.setDataXML(%s);
        myChart.render("chartdiv-%s");
        """
        retval = fusion_map
        for key in SHORT_NAME_TO_ID.values():
            retval += chart_map % ('xmlChartData', key)
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
        param_setter = lambda params, x: params.__setitem__(x, getattr(self.context, 'map_' + x) or self.default_params.get(x))
        for key in self.default_params:
            param_setter(params, key)
        return params

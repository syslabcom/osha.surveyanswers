from zope.interface import implements
from Products.Archetypes.Widget import StringWidget, IntegerWidget, \
    SelectionWidget
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from pkg_resources import resource_listdir #@UnresolvedImport
from zope.component import adapts #@UnresolvedImport
from osha.surveyanswers.subtypes.interfaces import IAnswers
import os
from Products.Archetypes.Field import StringField, IntegerField

class MyMapBorderColorField(ExtensionField, StringField):
    """The border color of the map"""
    name = 'map_border_color'

class MyMapFillColorField(ExtensionField, StringField):
    """The fill color of the map"""
    name = 'map_fill_color'

class MyMapNumberSuffixField(ExtensionField, StringField):
    """The number suffix for the labels of the map"""
    name = 'map_number_suffix'

class MyMapLabelSepCharField(ExtensionField, StringField):
    """The separator of label and number of the map"""
    name = 'map_label_sep_char'

class MyMapBaseFontSizeField(ExtensionField, IntegerField):
    """The font size of the map labels """
    name = 'map_base_font_size'

class MyMapMapField(ExtensionField, StringField):
    """The map itself """
    name = 'map_map_name'

class BlobExtender(object):
    adapts(IAnswers)
    implements(ISchemaExtender)
    fields = []
    field_adder = lambda fields, field, widget: fields.append(field(field.name, #@UndefinedVariable
                                                              widget=widget(label=field.__doc__),
                                                              schemata="Survey configuration"))
    field_adder(fields, MyMapBorderColorField, StringWidget)
    field_adder(fields, MyMapFillColorField, StringWidget)
    field_adder(fields, MyMapNumberSuffixField, StringWidget)
    field_adder(fields, MyMapLabelSepCharField, StringWidget)
    field_adder(fields, MyMapBaseFontSizeField, IntegerWidget)
    field_adder(fields, MyMapMapField, SelectionWidget)
    maps = resource_listdir(__module__, #@UndefinedVariable
                         os.path.join('..', 'browser', 'resources', 'flash'))
    maps.sort()
    fields[-1].vocabulary = maps
    
    def __init__(self, context):
        self.context = context
        
    def getFields(self):
        return self.fields

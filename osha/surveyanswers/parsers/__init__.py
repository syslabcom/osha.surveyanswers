from StringIO import StringIO #@UnresolvedImport
import csv #@UnresolvedImport
import random #@UnresolvedImport

SHORT_NAME_TO_ID = dict((
        ('AL', '001'),
        ('AD', '002'),
        ('AT', '003'),
        ('BY', '004'),
        ('BE', '005'),
        ('BA', '006'),
        ('BG', '007'),
        ('HY', '008'),
        ('CZ', '009'),
        ('DK', '010'),
        ('EE', '011'),
        ('FI', '012'),
        ('FR', '013'),
        ('DE', '014'),
        ('GR', '015'),
        ('HU', '016'),
        ('IS', '017'),
        ('IE', '018'),
        ('IT', '019'),
        ('LV', '020'),
        ('LI', '021'),
        ('LT', '022'),
        ('LU', '023'),
        ('MK', '024'),
        ('MT', '025'),
        ('MD', '026'),
        ('MC', '027'),
        ('MO', '028'),
        ('NL', '029'),
        ('NO', '030'),
        ('PL', '031'),
        ('PT', '032'),
        ('RO', '033'),
        ('SM', '034'),
        ('CS', '035'),
        ('SK', '036'),
        ('SL', '037'),
        ('ES', '038'),
        ('SE', '039'),
        ('CH', '040'),
        ('UA', '041'),
        ('UK', '042'),
        ('VA', '043'),
        ('CY', '044'),
        ('TK', '045'),
        ('RU', '046'),
        ('SC', '047'),
        ('EN', '048'),
        ('NI', '049'),
        ('WA', '048'),
)) 

SHORT_NAME_TO_LONG = dict((
        ('AL', 'Albania'),
        ('AD', 'Andorra'),
        ('AT', 'Austria'),
        ('BY', 'Belarus'),
        ('BE', 'Belgium'),
        ('BA', 'Bosnia-Herzegovina'),
        ('BG', 'Bulgaria'),
        ('HY', 'Croatia'),
        ('CZ', 'Czech Republic'),
        ('DK', 'Denmark'),
        ('EE', 'Estonia'),
        ('FI', 'Finland'),
        ('FR', 'France'),
        ('DE', 'Germany'),
        ('GR', 'Greece'),
        ('HU', 'Hungary'),
        ('IS', 'Iceland'),
        ('IE', 'Ireland'),
        ('IT', 'Italy'),
        ('LV', 'Latvia'),
        ('LI', 'Liechtenstein'),
        ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
        ('MK', 'Macedonia'),
        ('MT', 'Malta'),
        ('MD', 'Moldova'),
        ('MC', 'Monaco'),
        ('MO', 'Montenegro'),
        ('NL', 'Netherlands'),
        ('NO', 'Norway'),
        ('PL', 'Poland'),
        ('PT', 'Portugal'),
        ('RO', 'Romania'),
        ('SM', 'San Marino'),
        ('CS', 'Serbia'),
        ('SK', 'Slovakia'),
        ('SL', 'Slovenia'),
        ('ES', 'Spain'),
        ('SE', 'Sweden'),
        ('CH', 'Switzerland'),
        ('UA', 'Ukraine'),
        ('UK', 'United Kingdom'),
        ('VA', 'Vatican City'),
        ('CY', 'Cyprus'),
        ('TK', 'Turkey'),
        ('RU', 'Russia'),
        ('SC', 'Scotland'),
        ('EN', 'England'),
        ('NI', 'North Ireland'),
        ('WA', 'Wales'),
)) 

SINGLE_DATASET = """
  <entity id = '%(shortname)s' 
          value = '%(value)s'
          link='%(question)s/%(shortname)s' /" + ">""".replace('\n', '')

def getShortNameById(id):
    for key, value in SHORT_NAME_TO_ID.items():
        if int(value) == id:
            return key
        
def country_extractor(context, results): 
    #data = csv.reader(StringIO(string), 'excel-tab')
    #data.next()
    for key, value in SHORT_NAME_TO_ID.items():
        yield (SINGLE_DATASET % ({'shortname' : SHORT_NAME_TO_ID.get(key, ''), 
                                  'value' : "%02.2f" % (results.get(int(value), 0) * 100),
                                  'question' : context}))

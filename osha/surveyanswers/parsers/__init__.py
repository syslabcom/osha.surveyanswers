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

SINGLE_DATASET = """
  <entity id = '%(shortname)s' 
          value = '%(value)s'
          link='JavaScript:drilldown(\\"%(shortname)s\\");' /" + ">""".replace('\n', '')

def extractor(string): 
    #data = csv.reader(StringIO(string), 'excel-tab')
    #data.next()
    for row in SHORT_NAME_TO_ID.keys():
        yield SINGLE_DATASET % ({'shortname' : SHORT_NAME_TO_ID.get(row, ''),
                                      'value' : int(random.random() * 100)})

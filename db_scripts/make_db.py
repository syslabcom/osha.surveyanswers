# This simple script helps to create a simple local database with random data.
# To use it, configure osha to use sqlite, you can do that here:
# http://127.0.0.1:5040/test/osha-database-controlpanel
# The database name will be the file to which the sql data is stored
# You then create the random data with this script, and feed this data into
# sqlite:
# sqlite3 your_db < db_setup.sql
# Creating the sample data takes some time, as does adding into the local db

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

ID_TO_SHORT_NAME = dict([(x[1], x[0]) for x in SHORT_NAME_TO_ID.items()])

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

ID_TO_LONG_NAME = dict([(x[0], SHORT_NAME_TO_LONG[x[1]]) for x in ID_TO_SHORT_NAME.items()])

import random

tmpl1 = 'create table responses (id SERIAL PRIMARY KEY, %s);\n'
tmpl2 = 'insert into responses (%s) values (%s);\n'

bias = 0
new_bias = 0

class Bla:
    def __init__(self):
        self.bias = 0
        self.new_bias = 0
    def biased_rand(self):
        if not self.new_bias:
           self.new_bias = random.randint(100, 1000)
           self.bias = random.randint(-2 * 4, 2 * 4)
        self.new_bias -= 1
        return str(min(2 ** 5, max(0, (random.randint(0, 2 **5) + self.bias))))

bla = Bla()

out = file('db_setup.sql', 'w')
out.write('drop table responses;\n')
out.write(tmpl1 % ', '.join(['question_%i INTEGER' % x for x in range(100)]))
for i in range(1000):
    out.write(tmpl2 % (', '.join(['question_%i' % x for x in range(100)]), ', '.join([bla.biased_rand() for x in range(100)])))

out.write('drop table questions;\n')
out.write('create table questions(id SERIAL PRIMARY KEY, question_field TEXT, question TEXT, question_group TEXT, is_country INTEGER, is_designator INTEGER, type INTEGER, show_which INTEGER, show_which_text TEXT, hide_question INTEGER);\n')
out.write('drop table answer_meanings;\n')
out.write('create table answer_meanings(id SERIAL PRIMARY KEY, question_id INTEGER, answer_bit INTEGER, answer_text TEXT, position INTEGER);\n')
out.write('drop table map_data;\n')
out.write('create table map_data(id SERIAL PRIMARY KEY, question_id INTEGER, rng1_num INTEGER, rng1 TEXT, rng2_num INTEGER, rng2 TEXT, rng3_num INTEGER, rng3 TEXT);\n')
out.write('insert into questions (question_field, question, question_group, is_country, is_designator, type, show_which, show_which_text, hide_question) values (\'question_0\', \'country\', \'group country\', 1, 0, 0, 1, \'Show which text\', 0);\n')
for i in range(1, 49):
    country = ID_TO_LONG_NAME.get('%03i' % i)
    out.write('insert into answer_meanings (question_id, answer_bit, answer_text, position) values (0, %i, \'%s\', %i);\n' % (i, country, i))

getGroup = lambda: random.sample(['Group%i' % x for x in range(1, 8)], 1)[0]
def addType1(question):
    rand = lambda: random.sample(('yes', 'no', 'maybe'), 1)[0]
    position = 0
    for answer_bit, answer_text in [(1, 'yes'),(2, 'maybe'),(4, 'no')]:
        out.write('insert into answer_meanings (question_id, answer_bit, answer_text, position) values(%i, %i, \'%s\', %i);\n' % (question, answer_bit, answer_text, position))
        position += 1
    out.write('insert into map_data (question_id, rng1_num, rng1, rng2_num, rng2, rng3_num, rng3) values(%i, %i, \'%s\', %i, \'%s\', %i, \'%s\');\n' % (question, 20, "Small agreement", 50, "Medium agreement", 80, "High agreement"))

def addType2(question):
    position = 0
    for answer_bit in [1,2,4,8,16]:
        out.write('insert into answer_meanings (question_id, answer_bit, answer_text, position) values(%i, %i, \'answer %i\', %i);\n' % (question, answer_bit, answer_bit, position))
        position += 1
    out.write('insert into map_data (question_id, rng1_num, rng1, rng2_num, rng2, rng3_num, rng3) values(%i, %i, \'%s\', %i, \'%s\', %i, \'%s\');\n' % (question, 20, "Small agreement", 50, "Medium agreement", 80, "High agreement"))

def addType3(question):
    position = 0
    for answer_bit, answer_text in [(1,'up to one'), (2, 'up to two'), (4, 'up to three'), (8, 'up to four'), (16, 'up to five')]:
        out.write('insert into answer_meanings (question_id, answer_bit, answer_text, position) values(%i, %i, \'%s\', %i);\n' % (question, answer_bit, answer_text, position))
        position += 1
    out.write('insert into map_data (question_id, rng1_num, rng1, rng2_num, rng2, rng3_num, rng3) values(%i, %i, \'%s\', %i, \'%s\', %i, \'%s\');\n' % (question, 20, "Small agreement", 50, "Medium agreement", 80, "High agreement"))

types = {}
types['0'] = addType1
types['1'] = addType2
types['2'] = addType3

for i in range(1, 11):
    question_type = random.sample('012', 1)[0]
    question_name = ' '.join(random.sample(('foo', 'bar', 'baz', 'foobar'), 3))
    out.write('insert into questions (question_field, question, question_group, is_country, is_designator, type, show_which, show_which_text, hide_question) values (\'question_%i\', \'%s\', \'%s\', 0, 1, \'%s\', 1, \'show which text\', 0);\n' % (i, question_name, "Discriminator question", question_type))
    types[question_type](i)

for i in range(10, 100):
    question_type = random.sample('012', 1)[0]
    question_name = ' '.join(random.sample(('foo', 'bar', 'baz', 'foobar', 'foobaz', 'barbaz'), 6)) 
    out.write('insert into questions (question_field, question, question_group, is_country, is_designator, type, show_which, show_which_text, hide_question) values (\'question_%i\', \'%s\', \'%s\', 0, 0, \'%s\', 1, \'Show which text\', 0);\n' % (i, question_name, getGroup(), question_type))
    types[question_type](i)


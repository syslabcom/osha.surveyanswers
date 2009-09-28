import os
import re
import xlrd
country_infix = re.compile('6204(.*)TRA_final.xls')
country_code_mapping = {'CZX' : 'cs',
                        'CZE' : 'cs',
                        'LUF' : 'ignore',
                        'FRX' : 'fr',
                        'FRE' : 'fr',
                        'EEE' : 'et',
                        'EST' : 'es',
                        'MTM' : 'mt',
                        'SIX' : 'sl',
                        'SLV' : 'sl',
                        'SEX' : 'sv',
                        'SWE' : 'sv',
                        'CYX' : 'ignore',
                        'LUG' : 'ignore',
                        'CHG' : 'ignore',
                        'HRX' : 'hr',
                        'DEX' : 'de',
                        'GER' : 'de',
                        'ROX' : 'ro',
                        'ROM' : 'ro',
                        'ITX' : 'it',
                        'ITA' : 'it',
                        'CHI' : 'ignore',
                        'MTE' : 'ignore',
                        'LTX' : 'lt',
                        'LIT' : 'lt',
                        'NWX' : 'no',
                        'ELX' : 'el',
                        'GRE' : 'el',
                        'NLX' : 'nl',
                        'DUT' : 'nl',
                        'BEN' : 'ignore',
                        'TRX' : 'tr',
                        'ATX' : 'ignore',
                        'BEF' : 'ignore',
                        'SKX' : 'sk',
                        'SLK' : 'sk',
                        'PLX' : 'pl',
                        'POL' : 'pl',
                        'EER' : 'ru',
                        'FIS' : 'ignore',
                        'LUL' : 'lb',
                        'LUE' : 'ignore',
                        'HUX' : 'hu',
                        'HUN' : 'hu',
                        'IEX' : 'ignore',
                        'FIF' : 'fi',
                        'FIN' : 'fi',
                        'DKX' : 'da',
                        'DAN' : 'da',
                        'PTX' : 'pt',
                        'POR' : 'pt',
                        'CHF' : 'ignore',
                        'ESX' : 'es',
                        'SPA' : 'es',
                        'BGX' : 'bg',
                        'BUL' : 'bg',
                        'LVL' : 'lv',
                        'LAT' : 'lv',
                        'LVR' : 'ignore',
                        'UKX' : 'en'}
language_mapping = {'CZX' : 'Czech',
                    'FRX' : 'French',
                    'EEE' : 'Estonian',
                    'MTM' : 'Maltese',
                    'SIX' : 'Slovenian',
                    'SEX' : 'Swedish',
                    'HRX' : 'Croatian',
                    'DEX' : 'German',
                    'ROX' : 'Romanian',
                    'ITX' : 'Italian',
                    'LTX' : 'Lithuanian',
                    'NWX' : 'Norwegian',
                    'ELX' : 'Greek',
                    'NLX' : 'Dutch',
                    'TRX' : 'Turkish',
                    'SKX' : 'Slovak',
                    'PLX' : 'Polish',
                    'EER' : 'Russian',
                    'LUL' : 'Luxembourgish',
                    'HUX' : 'Hungarian',
                    'FIF' : 'Finnish',
                    'DKX' : 'Danish',
                    'PTX' : 'Portuguese',
                    'ESX' : 'Spanish',
                    'BGX' : 'Bulgarian',
                    'LVL' : 'Latvian',
                    'UKX' : 'English'}

po_template = """
msgid ""
msgstr ""

"Project-Id-Version: osha.surveyanswers\\n"
"POT-Creation-Date: 2009-09-04 23:20+0000\\n"
"PO-Revision-Date: 2009-09-04 23:22+0100\\n"
"Last-Translator: Patrick Gerken <gerken@syslab.com>\\n"
"Language-Team: Syslab.com GmbH <info@syslab.com>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=1; plural=0;\\n"
"Language-Code: %(code)s\\n"
"Language-Name: %(language)s\\n"
"Preferred-Encodings: utf-8 latin1\\n"
"Domain: osha.surveyanswers\\n"
"""

def sanitize(data):
    return unicode(data.value).strip().replace('"', '\\"').replace("\n", " ")
for filename in [x for x in os.listdir('.') if x.endswith('final.xls')]:
    country_code = country_infix.findall(filename)[0]
    country = country_code_mapping[country_code]

    if country == 'ignore':
        continue
    language = language_mapping[country_code]
    translations = {}
    xls_file = xlrd.open_workbook(filename)
    sheet = xls_file.sheet_by_name('TRANSLATION')
    for row_id in range(sheet.nrows):
        row = sheet.row(row_id)
        for cell_id in range(18):
            if row[cell_id].value and row[cell_id + 36].value and row[cell_id].value != row[cell_id + 36].value:
                translations[sanitize(row[cell_id])] = sanitize(row[cell_id + 36])
            if cell_id == 1 and (row[cell_id].value.startswith('MM') or row[cell_id].value.startswith('ER')):
                question = sanitize(row[2])
            if cell_id == 3 and row[cell_id].value:
                translations[question + " " + sanitize(row[cell_id])] = translations.get(question, question) + " " + sanitize(row[cell_id + 36])

    path = './locales/%s' % country
    os.mkdir(path)
    os.mkdir(path + '/LC_MESSAGES')

    lang_file = file(path + '/LC_MESSAGES/osha.surveyanswers.po', 'w')
    lang_file.write(po_template % {'code' : country, 
                                   'language' : language})
    for key, translation in translations.items():
        lang_file.write(('msgid "%s"\n' % key).encode('utf-8'))
        lang_file.write(('msgstr "%s"\n' % translation).encode('utf-8'))

xls_file = xlrd.open_workbook('question_group_translations.xls')
sheet = xls_file.sheet_by_name('Sheet1')

translations = sheet.row(0)
originals = {}
for row_id in range(1, sheet.nrows):
    originals[sheet.cell(row_id, 1).value] = row_id

for translation_column in range(2, sheet.ncols):
    key = translations[translation_column].value
    if key == 'MAL':
        continue
    lang_code = country_code_mapping[key]
    if lang_code == 'ignore':
        raise key
    lang_file = file('./locales/%s/LC_MESSAGES/osha.surveyanswers.po' % lang_code, 'a')
    for original, translation_row in originals.items():
        translation = sheet.cell(translation_row, translation_column).value
        lang_file.write(('msgid "%s"\n' % original).encode('utf-8'))
        lang_file.write(('msgstr "%s"\n' % translation).encode('utf-8'))

    


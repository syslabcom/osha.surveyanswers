import os
import re
import xlrd
country_infix = re.compile('6204(.*)TRA_final.xls')
country_code_mapping = {'CZX' : 'cz'}
language_mapping = {'CZX' : 'Czech'}

po_template = """
msgid ""
msgstr ""

"Project-Id-Version: osha.surveyanswers\n"
"POT-Creation-Date: 2009-09-04 23:20+0000\n"
"PO-Revision-Date: 2009-09-04 23:22+0100\n"
"Last-Translator: Patrick Gerken <gerken@syslab.com>\n"
"Language-Team: Syslab.com GmbH <info@syslab.com>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=1; plural=0;\n"
"Language-Code: %(code)s\n"
"Language-Name: %(language)s\n"
"Preferred-Encodings: utf-8 latin1\n"
"Domain: DOMAIN\n"
"""
for filename in [x for x in os.listdir('.') if x.endswith('final.xls')]:
    country_code = country_infix.findall(filename)[0]
    country = country_code_mapping[country_code]
    language = language_mapping[country_code]
    translations = {}
    xls_file = xlrd.open_workbook(filename)
    sheet = xls_file.sheet_by_name('TRANSLATION')
    for row_id in range(sheet.nrows):
        row = sheet.row(row_id)
        if row[2] == 'Country Code':
            import pdb;pdb.set_trace()
        if row[2].value:
            translations[row[2].value] = row[20].value

    lang_file = file('osha.surveyanswers_%s.po' % country, 'w')
    lang_file.write(po_template % {'code' : country, 
                                   'language' : language})
    for key, translation in translations.items():
        lang_file.write(('msgid "%s"\n' % key).encode('utf-8'))
        lang_file.write(('msgstr "%s"\n' % translation).encode('utf-8'))


        

    

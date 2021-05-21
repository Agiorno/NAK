import requests
import os
import docx2txt
from pdf2docx import parse
from striprtf.striprtf import rtf_to_text
import codecs

class Parse:
    
    def parse_docx(self, file):
        my_file = docx2txt.process('text.docx')
        my_file = my_file.replace('\n',' ').replace('\t','').replace('\xa0','').replace('’', "'").lower()
        os.remove('text.docx')
        return my_file

    def parse_pdf(self, file):
        parse('text.pdf', 'text.docx', start=1, end=None)
        my_file = docx2txt.process('text.docx')
        my_file = my_file.replace('\n',' ').replace('\t','').replace('\xa0','').replace('’', "'").lower()
        os.remove('text.docx')
        os.remove('text.pdf')
        return my_file
        
    def parse_rtf(self, file):
        rtf = open('text.rtf').read()
        text = rtf_to_text(rtf)
        a = codecs.encode(text, encoding='latin-1', errors='ignore')
        t = codecs.decode(a, encoding='cp1251')
        t = t.strip()
        t = t.replace('’', "'").lower()
        os.remove('text.rtf')
        return t

    def download_file(self, link):
        response = requests.get(link)
        self.extension = response.headers['Content-Disposition'].split('"')[1].split('.')[1]
        name = f'text.{self.extension}'
        with open(name, 'wb') as f:
            f.write(response.content)
        if self.extension == 'docx':
            text = self.parse_docx('text.docx')
        elif self.extension == 'pdf':
            text = self.parse_pdf('text.pdf')
        elif self.extension == 'rtf':
            text = self.parse_rtf('text.rtf')
        else:
            pass
        return text

import docx2txt
import requests
import os
import urllib.parse
from bs4 import BeautifulSoup as bs


class Analizator:
    
    counter = 0
    # передаем ссылку на законопроект и файл с тегами
    def __init__(self, link, tag_file):
        self.link = link
        print(self.link)
        self.tag_file = tag_file
        with open(self.tag_file, 'r') as f:
            tags = f.read()
        self.tags = tags.replace('\n',',').lower().strip().split(',')

        r = requests.get(self.link)
        soup = bs(r.text, 'html.parser')
        tables = soup.find_all('table')
       
     
        
        Analizator.counter +=1
        
        
        
        try:
            dts = []
            for i in soup.find_all('div', attrs={'class':"zp-info"})[0].find_all('dt'):
                dts.append(i.text)
            ind = dts.index('Текст законопроекту та супровідні документи:')
            
            li = []
            lis = soup.find_all('div', attrs={'class':"zp-info"})[0].find_all('dd')[ind].find_all('li')
            for i in lis:
                li.append(i.text.lower())
            for i in li:
                if i.find('проект')>=0:
                    num = li.index(i)
            try:
                path = lis[num].find('a')['href']
                self.file_link = 'http://w1.c1.rada.gov.ua/pls/zweb2/'+path

                the_book = requests.get(self.file_link, stream=True)
                
                extension = the_book.headers['Content-Disposition'].split('"')[1].split('.')[1]
                if extension == 'rtf':
                    self.status = 'rtf'
                elif extension == 'docx' or extension =='doc':
                    with open('text.docx', 'wb') as f:
                        for chunk in the_book.iter_content(1024 * 1024 * 2):  # 2 MB chunks
                            f.write(chunk)

                    file = docx2txt.process('text.docx')

                    self.file = file.replace('\n',' ').replace('\t','').replace('\xa0','').lower()

                    result = []
                    for tag in self.tags:
                        position  = self.file.find(tag)
                        if position>=0:
                            q = ''
                            for i in tag.split():
                                q=q+i.capitalize()
                            tag = '#'+q.strip()
                            tag = tag.replace(tag[0], tag[0].lower(), 1)
                            result.append(tag)
                    self.status = 'ok'
                    self.result = result
                elif extension == 'pdf':
                    self.status = 'pdf'
                else:
                    self.status = 'wrong extension'
            except TypeError:
                self.status = 'no_file'
                # print('ERROR: No file has attached')    
   
        except:
            self.status = 'error'
        
        print(self.status)

def get_links(num):
    d = []
   
    try:
        link = f'http://w1.c1.rada.gov.ua/pls/zweb2/webproc2_5_1_J?ses=10010&num_s=2&num={str(num)}&date1=&date2=&name_zp=&out_type=&id='
        r= requests.get(link)
        soup = bs(r.text, 'html.parser')
        tr = soup.find_all('table')[0].find_all('tr')
        if len(tr)>1:
            for i in range(1, len(tr)):
                link = f"http://w1.c1.rada.gov.ua/pls/zweb2/{tr[i].contents[1].find('a')['href']}"
                d.append(link)
    except:
        pass
    return d

def get_atrrs(link):
    r = requests.get(link)
    soup = bs(r.text, 'html.parser')
    target = soup.find_all('div', attrs={'class':'information_block_ins'})
    name = target[1].find('h3').text
    target = soup.find_all('div', attrs={'class':'zp-info'})
    dts = []
    for i in target[0].find_all('dt'):
        dts.append(i.text)
    ind = dts.index('Номер, дата реєстрації:')   
    number = target[0].find_all('dd')[ind].text
    return name, number
       
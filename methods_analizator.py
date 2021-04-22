import docx2txt
import requests
import os
import urllib.parse
from bs4 import BeautifulSoup as bs
from datetime import date
from time import sleep
import concurrent.futures as cf

class AnalizatorMethod:


    tag_file = 'tags'
    with open(tag_file,'r') as f:
        tags = f.read()
    tags = tags.replace('\n',',').lower().strip().split(',')
   
    root = 'http://w1.c1.rada.gov.ua/pls/zweb2/'

    def make_soup(self, link):
        print(f'link={link}')
        r = requests.get(link, timeout=1)
        soup = bs(r.text, 'html.parser')
        print('soup is ready')
        return soup
        

    def check_if_file_exist(self, soup):
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
            file_link = f'{self.root}{path}'
        except TypeError:
            file_link = ''
        return file_link

    def get_extension(self, response):

        extension = response.headers['Content-Disposition'].split('"')[1].split('.')[1]
        
        return extension

    def docx_analize(self, _file):

        with open('text.docx', 'wb') as f:
                for chunk in _file.iter_content(1024 * 1024 * 2):  # 2 MB chunks
                    f.write(chunk)
        
        my_file = docx2txt.process('text.docx')
        

        my_file = my_file.replace('\n',' ').replace('\t','').replace('\xa0','').lower()
        

        result = self.find_tags(my_file)
        
        os.remove('text.docx')
        
        return result
    
    def make_concat_search_link(self, date_finish='',date_start=None):
        link = self.make_search_link(date_finish='',date_start=None)
        r = requests.get(link, timeout=1)
        soup = bs(r.text, 'html.parser')
        cnt = soup.find('div', attrs= {'class':'information_block_ins'}).find('a').text.split(': ')[1].strip()
        page = 1
        link = f'{link}&page={page}&zp_cnt={cnt}'
        return link

    def make_search_link(self, date_start=None, date_finish = ''):
        if date_start == None:
            today = date.today()
            my_date = today.strftime('%m.%Y') 
            date_start = f'01.{my_date}'
        link = f'{self.root}webproc2_5_1_J?ses=10010&num_s=2&num=&date1={date_start}&date2={date_finish}&name_zp=&out_type=&id='
        return link
    
    def analize_name(self, td):
        try:
            link = td[0].find('a')['href']
            link = f'{self.root}{link}'
        except:
            link = ''
        number  = td[0].text
        date = td[1].text
        text = td[2].text
        result = {'link': link, 'number':number, 'date':date, 'text':text}
        return result

    def find_tags(self, text):
        result = []
        for tag in self.tags:
            position  = text.find(tag)
            if position>=0:
                
                q = ''
                for i in tag.split():
                    q=q+i.capitalize()
                tag = '#'+q.strip()
                tag = tag.replace(tag[0], tag[0].lower(), 1)
                result.append(tag)
        return result
    
    def make_dict_from_name(self,tr,position):
        td = tr[position].find_all('td')
        my_dict = self.analize_name(td)
        my_dict['tags'] = self.find_tags(my_dict['text'])
        return my_dict

    def get_links(self, num):
        d = []

        try:
            link = f'{self.root}webproc2_5_1_J?ses=10010&num_s=2&num={str(num)}&date1=&date2=&name_zp=&out_type=&id='
            soup  = self.make_soup(link)
            tr = soup.find_all('table')[0].find_all('tr')
            if len(tr)>1:
                for i in range(1, len(tr)):
                    link = f"{self.root}{tr[i].contents[1].find('a')['href']}"
                    d.append(link)
        except:
            pass
        return d

    def get_atrrs(self, link):
        soup  = self.make_soup(link)
        target = soup.find_all('div', attrs={'class':'information_block_ins'})
        name = target[1].find('h3').text
        target = soup.find_all('div', attrs={'class':'zp-info'})
        dts = []
        for i in target[0].find_all('dt'):
            dts.append(i.text)
        ind = dts.index('Номер, дата реєстрації:')   
        number = target[0].find_all('dd')[ind].text
        return name, number

# class Analizator(AnalizatorMethod):
    
#     def __init__(self, link):
        

#         print('start making soup')
#         # soup = self.make_soup(link)
#         print(f'link={link}')
#         r = requests.get(link)
#         soup = bs(r.text, 'html.parser')
#         # print('soup is ready')
#         print('soup is ready')
#         try:
#             file_link = self.check_if_file_exist(soup)
#             self.file_link  = file_link
            
#             if file_link != '':
#                 the_file = requests.get(file_link, stream=True)
#                 extension = self.get_extension(the_file)
                
#                 if extension == 'docx' or extension =='doc':
#                     self.status = 'ok'
#                 elif extension == 'rtf':
#                     self.status = 'rtf'                
#                 elif extension == 'pdf':
#                     self.status = 'pdf'
#                 else:
#                     self.status = 'wrong extension'
#             else:
#                 self.status = 'no_file' 

#         except:
#             self.status = 'error'
#             self.file_link == ''  

        

# class CheckNewBills(AnalizatorMethod):
#     def __init__(self):

#         link = self.make_concat_search_link()
#         r = requests.get(link, timeout=1)
#         soup = bs(r.text, 'html.parser')
#         self.tr = soup.find_all('tr')

#     def check_tags_in_names(self):

#         bills = []
#         no_tags = 0
#         with_tags =0
#         for i in range(1, len(self.tr)):
#             my_dict = self.make_dict_from_name(self.tr, i)
#             if len(my_dict['tags']) == 0:
#                 no_tags+=1
#             else:
#                 with_tags+=1
#             bills.append(my_dict)
#         print(f'links -> {len(bills)}')
#         print(f'names with no tags -> {no_tags}')
#         print(f'names with tags -> {with_tags}')

#         return bills


#     def sorted_arrays(self, bills):       
#         else_links = []
#         docx_links = []
#         for bill in bills:
#             a = Analizator(bill['link'])
#             bill['file_link'] = a.file_link
#             bill['status'] = a.status
#             if a.status == 'ok':
#                 docx_links.append(bill)
#             else:
#                 else_links.append(bill)
#         return else_links, docx_links


#     def answer(self):
#         bills = self.check_tags_in_names()
#         else_links, docx_links = self.sorted_arrays(bills)
#         with_tags = []
#         for i in docx_links:
#             the_file = requests.get(i['file_link'], stream=True)
#             result = self.docx_analize(the_file)
#             if len(result)>0:
#                 i['tags'] = result
#                 with_tags.append(i)
#         print(self.timeout_links)

#         message = f'''Всього опрацьовано {len(bills)} законопроектів.
#         *Виявлено тегів*: {len(with_tags)}'''
#         return message

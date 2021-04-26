import docx2txt
import requests
import os
import urllib.parse
from bs4 import BeautifulSoup as bs
from datetime import date, timedelta
from time import sleep
import concurrent.futures as cf
from pdf2docx import parse
import codecs
from striprtf.striprtf import rtf_to_text

class AnalizatorMethod:


    tag_file = 'tags'
    with open(tag_file,'r') as f:
        tags = f.read()
    tags = tags.replace('\n',',').lower().strip().split(',')
   
    root = 'http://w1.c1.rada.gov.ua/pls/zweb2/'

    def make_soup(self, link):
        r = requests.get(link, timeout=1)
        soup = bs(r.text, 'html.parser')
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

    def make_concat_search_link(self, date_finish='',date_start=None, yesterday = False):
        link = self.make_search_link(date_finish='',date_start=None, yesterday = False)
        r = requests.get(link, timeout=1)
        soup = bs(r.text, 'html.parser')
        cnt = soup.find('div', attrs= {'class':'information_block_ins'}).find('a').text.split(': ')[1].strip()
        page = 1
        link = f'{link}&page={page}&zp_cnt={cnt}'
        return link

    def make_search_link(self, yesterday = False, date_start=None, date_finish = ''):
        if date_start == None:
            today = date.today()
            yesterday = today - timedelta(days=1)
            if yesterday:
                date_start = yesterday.strftime('%d.%m.%Y')
            else:
                date_start = today.strftime('%d.%m.%Y') 
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
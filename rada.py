import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
from uuid import uuid4
from ninox import Ninox
import time

class Rada:
    

    def __init__(self, date, session, n):      
        self.date = str(date).replace('.','').strip()       
        self.session = str(session).strip()        
        self.n = n
        self.used_links = self.n.used_links()       
        self.rada_link = f'http://w1.c1.rada.gov.ua/pls/radan_gs09/ns_el_h2?data={self.date}&nom_s={self.session}'         
        self.list_for_laws = {}      
        self.list_for_votes = []
      
        self.links = []
               
        r = requests.get(self.rada_link)    
        soup = bs(r.text, 'html.parser')       
        table = soup.find_all('table', attrs={'class':'tab_1'})       
        self.tr = table[0].find_all('tr')      
        for i in range(4, len(self.tr)):
            if self.tr[i].text.find('Утрималось')>=0:
                vote = 'http://w1.c1.rada.gov.ua'+self.tr[i].find_all('td')[3].find_all('a')[-1]['href'].replace('ns_golos','ns_golos_print')+'&vid=1'
                if vote not in self.used_links: # Сравниваем с ниноксом и добавляем новые
                    l = {i:vote}
                    self.links.append(l)
       
        
        
        
class Votes:    
    
    
    error_list = []
    
    def __init__(self, link,list_for_laws,list_for_votes, date):
        self.key = list(link.keys())[0]
        self.link = list(link.values())[0]
        self.list_for_laws = list_for_laws
        self.list_for_votes = list_for_votes
        x = str(date).replace('.','').strip()
        self.date = f'{x[4:]}-{x[2:4]}-{x[:2]}'
       
        
        r = requests.get(self.link)
        soup = bs(r.text, 'html.parser')
        table = soup.find_all('table')
        
        a = table[0].find_all('b')[2].text.strip().split('про ')
        
        while a == ['']: # если массив пустой - значит сайт еще не подгрузился и мы ждем минуту
            logger.warning('РАДА не подгрузилась, жду 30 секунд')
            time.sleep(30)
            table = my_soup(self.link)
            a = table[0].find_all('b')[2].text.strip().split('про ')
        
        self.a = a
        self.mp = table[1].find_all('td', attrs={'class':'hcol1'})
                    

    def mps_parcer(self):
    
    
        keywords = {'порядку денного': "Процедурне рішення",
               'поправк': "Поправка",
               'роцедур':"Процедурне рішення",
               'короченн': "Процедурне рішення"}

        try:
            if len(self.a)>3: # если в массиве больше трех элементов, значит в названии закона есть "про" ...
                z = self.a[2].strip() # ... и мы соединяем все элементы с третьим
                for x in range(3, len(self.a)):
                    z = z+" про "+self.a[x].strip()
                di = {'Type': self.a[1].strip(), 'Name':z.strip()}
            elif len(self.a)==2: # Это всякие не законы - постановы и т.д
                di = {'Type': '', 'Name':self.a[0].strip()+' про '+self.a[1].strip()}
            else: # Это обычный закон
                di = {'Type': self.a[1].strip(), 'Name':self.a[2].strip()}

            # дальше из текста забираем семантику - номер и решение если такие есть
            self.a = di['Name'].split('(№')
            if len(self.a)>1:
                number = self.a[-1].split(')')[0].strip()
                level = self.a[-1].split(')')[1].replace('-','').strip()    
                di['Name'] = self.a[0].strip()
            else:
                number = ''
                level = ''

            for i in keywords.keys():
                if di['Type'].find(i)>=0:
                    level = keywords.get(i)
                elif di['Name'].find(i)>=0:
                    level = keywords.get(i)
            if level == '':
                if di['Type'].find('проект')>=0:
                    level = "за проект"
                else:
                    level = "інше"

            di['full_name'] = di['Name'].split(" - ")[0].strip()
            di['Number'] = number
            di['Level'] = level 
            di['UID'] = str(uuid4())
            di['Date_votes'] = self.date
            di['URL_votes'] = self.link

        except Exception as e:
            
            if hasattr(e, 'message'):
                
                error = e.message
                
            else:
                
                error = e
                
            log = {'link':self.link, 'error':error}
            error_list.append(log)
            
            di = {}

        self.di = di
        self.list_for_laws[self.key] = self.di
        
    def collect_mps(self):

        votes_var = {'Відсутн': "Відсутній",
               'Утри': "Утримався",
               'Не':"Не голосував"}

        try:
            for i in self.mp:                
                d1 = {'Short_name':i.text, 'Voting':i.next_sibling.next_sibling.text, 'UID': self.di['UID']}                
                for k in votes_var.keys():                    
                    if d1['Voting'].find(k)>=0:
                        d1['Voting'] = votes_var.get(k)                       
                self.list_for_votes.append(d1) # и к нему список голосов депутатов        

        except Exception as e:            
            if hasattr(e, 'message'):                
                error = e.message                
            else:                
                error = e                
            log = {'link':self.link, 'error':error}
            self.error_list.append(log)
         
    def worker(self):
        self.mps_parcer()
        self.collect_mps()
        
    

def worker(list_for_laws,list_for_votes,date, link):
    element = Votes(link,list_for_laws,list_for_votes,date)
    element.worker()
    

class Send:
    
    def __init__(self, laws, votes, n):
        self.laws= list(dict(sorted(laws.items(), key=lambda item: item[0])).values())
        self.votes = votes
        self.n = n
        self.my_schema = n.schema()
        
        
    def send_laws(self):
        df = pd.DataFrame(self.laws)
        full_names = df['full_name'].drop_duplicates().to_list()
        full_nums = df.drop_duplicates(subset='Name')['Number'].fillna('').to_list()
        h = self.n.get_from_ninox(self.my_schema['LAW'])['Name'].to_list()
        new_law_names = []
        for i in full_names:
            if i not in h:
                di = {'fields':{'Name':i, 'Number':full_nums[full_names.index(i)]}}
                new_law_names.append(di)
        self.n.send_to_ninox(new_law_names, self.my_schema['LAW'])
        laws = self.n.get_from_ninox(self.my_schema['LAW'])[['id', 'Name']]
        laws.columns = ['law_id','full_name']
        df = pd.merge(df, laws, how = 'left')
        dogs = []
        for index, row in df.iterrows():
            di = {'fields':{'Name':row['Name'], 'Number':row['Number'], 'Law': row['law_id'], 'URL_votes':row['URL_votes'],'UID':row['UID'],'Level': row['Level'], 'Type':row['Type'], 'Date_votes':row['Date_votes']}}
            dogs.append(di)
        js = self.n.send_to_ninox(dogs, self.my_schema['Voting'])
 
        self.js = js

    def send_voting_zakon(self):
        ninox_mp = self.n.get_from_ninox(self.my_schema['mps'])[['id', 'Short_name']]
        kovalyovy = ninox_mp[ninox_mp.Short_name == 'Ковальов О.І.']['id'].to_list() # отдельно однофамильцы
        df = pd.DataFrame(self.votes)
        df = pd.merge(df, ninox_mp[ninox_mp.Short_name != 'Ковальов О.І.'], how='left')
        a = 2
        for index, row in df[df.Short_name == 'Ковальов О.І.'].iterrows():
            df.at[index, 'id'] = kovalyovy[self.n.odd(a)]
            a+=1
        votings = []
        for i in self.js.json():
            _id =i['id']
            fields = i['fields']['UID']
            di = {'ninox_id':_id, 'UID':fields}
            votings.append(di)
        names = pd.DataFrame(self.laws)
        vv = pd.DataFrame(votings)
        names = pd.merge(names, vv, how='left')
        df = pd.merge(df, names[['UID', 'ninox_id']], how = 'left')
        dogs = []
        for index, row in df.dropna().iterrows():
            di = {'fields':{'mps':row['id'],'Zakon':row['ninox_id'], 'Golos':row['Voting']}}
            dogs.append(di)
        js = self.n.send_to_ninox(dogs, self.my_schema['Voting_Zakon']) 

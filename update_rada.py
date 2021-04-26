from apscheduler.schedulers.blocking import BlockingScheduler
from parsing_process import Parse
from check_updates import CheckNewBills
from ninox import Ninox
import ast
import pandas as pd
from analizator import Analizator



with open("monkey", "r") as f:
    password = ast.literal_eval(f.read())
try:
    n = Ninox(password['Anton'])
    n.team = n.get_team()['NAK']
    n.database = n.get_database()['BOT']
    my_schema = n.schema()
except:
    n = Ninox(password['Nadin'])
    n.team = n.get_team()['NAK']
    n.database = n.get_database()['BOT']
    my_schema = n.schema()

try:
    q = Ninox(password['Anton'])
    q.team = q.get_team()['NAK']
    q.database = q.get_database()['CRM']
    q_schema = q.schema()
except:
    q = Ninox(password['Nadin'])
    q.team = q.get_team()['NAK']
    q.database = q.get_database()['CRM']
    q_schema = q.schema()
    
class Rada(CheckNewBills):
    used_links = 'used_links.txt'

    def __init__(self, yesterday = False):
        super().__init__()
        self.yesterday = yesterday
        
        
    def get_links(self):
        links = self.check_tags_in_names()

    def make_new_links(self, links):
        with open(self.used_links, 'r') as f:
            fl = f.read()
        new_links = []
        for i in links:
            if fl.find(i['link'])<0:
                new_links.append(i)
        return new_links

    def send_with_tags(self):
        dogs = []
        for i in self.with_tags:
            di = {'fields':{'link': i['link'], 'number':i['number'], 'date':i['date'], 'text':i['text'], 'tags':i['tags'], 'Choice':1}}
            dogs.append(di)
        n.send_to_ninox(dogs, my_schema['links'])
        print(f'Выгружено {len(self.with_tags)} ссылок с тэгами')
        
    def send_no_files(self):
        dogs = []
        for i in self.to_check:
            di = {'fields':{'link': i['link'], 'number':i['number'], 'date':i['date'], 'text':i['text'], 'Choice':2}}
            dogs.append(di)
        n.send_to_ninox(dogs, my_schema['links'])
        print(f'Выгружено {len(self.to_check)} ссылок без файлов')
        
    def send_tags_in_name(self):
        dogs = [] 
        for i in self.find_tag_in_name:
            di = {'fields':{'link': i['link'], 'number':i['number'], 'date':i['date'], 'text':i['text'], 'tags':i['tags'], 'Choice':3}}
            dogs.append(di)
        n.send_to_ninox(dogs, my_schema['links'])
        print(f'Выгружено {len(self.find_tag_in_name)} ссылок с тегами в имени')
    
    def send_exceptions(self):   
        dogs = []
        for i in self.exception_links:
            di = {'fields':{'link': i['link'], 'number':i['number'], 'date':i['date'], 'text':i['text'], 'Choice':4}}
            dogs.append(di)
        n.send_to_ninox(dogs, my_schema['links'])
        print(f'Выгружено {len(self.exception_links)} ссылок с ошибками (ТАЙМАУТ)')

    def make_used_links(self):
        used_links = []
        for i in self.no_tags:
            used_links.append(i['link'])                
        for i in self.with_tags:
            used_links.append(i['link'])

        with open('used_links.txt', 'a') as f:
            f.writelines(used_links)
            f.close()
    
    def get_links_to_check(self):
        today_table = n.get_from_ninox(my_schema['links'])
        list_to_check = today_table.loc[(today_table.Choice == 'no file') | (today_table.Choice == 'errors'), 'link'].to_list()
        short_table = today_table[['link','id']]
        self.dict_to_check = short_table.set_index('link').to_dict()['id']

        return list_to_check

    def check_from_list(self):
        my_list = self.get_links_to_check()
        for i in my_list:
            a = Analizator(i)
            if a.status == 'ok':
                n_id = self.dict_to_check[i]
                if len(a.result) == 0:
                    n.delete_record(my_schema['links'], n_id)
                else:
                    dogs = []
                    di = {'id':n_id, 'fields':{'tags':a.result, 'Choice':1}}
                    dogs.append(di)
                    n.send_to_ninox(dogs, my_schema['links'])
            else:
                pass



    

    def timed_j(self, link=None, yesterday=False):
        if link == None:
            link =  self.check_tags_in_names()
        new_links = self.make_new_links(link)
       
        if len(new_links)>0:
            self.check_links(new_links)
            print(f'[БЕЗ ФАЙЛОВ]: {len(self.to_check)} [БЕЗ ТЭГОВ]: {len(self.no_tags)} [С ТЭГАМИ]: {len(self.with_tags)} [ОШИБОК]: {len(self.exception_links)}')
            self.send_no_files()
            self.send_exceptions()
            self.send_tags_in_name()
            self.send_with_tags()
            self.make_used_links()
        else:
            pass
        


    
sched = BlockingScheduler()

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour='8-18')
@sched.scheduled_job('cron', day_of_week='mon-fri', hour='8-18')
def timed_job_day():
    Rada().timed_j()
    print('done')
@sched.scheduled_job('cron', day_of_week='mon-fri', hour='0')    
def timed_job_midnight():
    Rada().timed_j(yesterday=True)
    
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=23, minute=59)
def delete_file_content():
    Rada().check_from_list()
    with open('used_links.txt', 'w') as f:
        f.write('')
        f.close()
    print('donedone:))')

sched.start()
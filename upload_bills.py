import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from ninox import Ninox
import ast


with open("monkey", "r") as f:
    password = ast.literal_eval(f.read())
try:
    n = Ninox(password['Anton'])
    n.team = n.get_team()['NAK']
    n.database = n.get_database()['CRM']
except KeyError:
    n = Ninox(password['Nadin'])
    n.team = n.get_team()['NAK']
    n.database = n.get_database()['CRM']

my_schema = n.schema()
coms = n.get_from_ninox(my_schema['Committee'])[['Name', 'id']]
coms['Name'] = coms['Name'].str.replace('Комітет Верховної Ради України','')
coms = coms.set_index('Name').to_dict()['id']

mps = n.get_from_ninox(my_schema['mps'])[['full_name', 'id']]
mps = mps.set_index('full_name').to_dict()['id']

def send_info(link):
    my_schema = n.schema()
    my_list = ['Номер, дата реєстрації:', 'Редакція законопроекту:','Рубрика законопроекту:', "Суб'єкт права законодавчої ініціативи:",
          'Головний комітет:', 'Ініціатор(и) законопроекту:']
    r = requests.get(link)
    soup = bs(r.text, 'html.parser')
    tables = soup.find_all('table')
    info = soup.find_all('div', attrs={'class':'zp-info'})
    name = soup.find('h3', attrs={'align':'center'}).text
    chronology = tables[0]
    dt = info[0].contents[1].find_all('dt')
    dd = info[0].contents[1].find_all('dd')
    dts = []
    for i in dt:
        dts.append(i.text)
    name = soup.find('h3', attrs={'align':'center'}).text
    number = dd[dts.index(my_list[0])].text.split(" ")[0]
    date = dd[dts.index(my_list[0])].text.split(" ")[2]
    x = str(date).replace('.','').strip()
    date = f'{x[4:]}-{x[2:4]}-{x[:2]}'
    try:
        redaction = dd[dts.index(my_list[1])].text
    except:
        redaction =''
    rubrica = dd[dts.index(my_list[2])].text
    subject = dd[dts.index(my_list[3])].text
    main_committee = f'{dd[dts.index(my_list[4])].text.split("Комітет")[1]}'
    dogs = []
    di = {'fields':{'Name': name, 'Number':number, 'Date':date, 'Redaction':redaction,'Category':rubrica, 'Subject':subject,
                   'Committee': coms[main_committee], 'link':link}}
    dogs.append(di)
    
    response = n.send_to_ninox(dogs, my_schema['Bills'])
    response  = response.json()
    deps = []
    for i in dd[dts.index(my_list[5])].find_all('li'):
        deps.append(i.text.split(' (')[0])

    dogs = []
    for i in deps:
        try:
            di = {'fields':{'Bills': response[0]['id'], 'mps':mps[i]}}
            dogs.append(di)
        except KeyError:
            di = {'fields':{'Bills': response[0]['id'], 'Author':i}}
    n.send_to_ninox(dogs, my_schema['authors'])

    tr = chronology.find_all('tr')
    dogs = []
    for i in range(1,len(tr)):
        date = tr[i].contents[1].text
        x = str(date).replace('.','').strip()
        date = f'{x[4:]}-{x[2:4]}-{x[:2]}'
        status = tr[i].contents[3].text
        di = {'fields':{'Bills': response[0]['id'], 'Date':date, 'Status':status}}
        dogs.append(di)
    n.send_to_ninox(dogs, my_schema['Chronology'])
    
def get_links(array):
    if type(array)!=list:
        q = []
        q.append(str(array))
        array = q
        
    d = []
   
    for item in array:
        try:
            link = f'http://w1.c1.rada.gov.ua/pls/zweb2/webproc2_5_1_J?ses=10010&num_s=2&num={str(item)}&date1=&date2=&name_zp=&out_type=&id='
            r= requests.get(link)
            soup = bs(r.text, 'html.parser')
            tr = soup.find_all('table')[0].find_all('tr')
            if len(tr)>1:
                for i in range(1, len(tr)):
                    link = f"http://w1.c1.rada.gov.ua/pls/zweb2/{tr[i].contents[1].find('a')['href']}"
                    d.append(link)
        except:
            print(item)
    return d



class Bills():
    
    my_schema = n.schema()
    
    def __init__(self):
        self.all_bills = n.get_from_ninox(self.my_schema['Bills'])
        self.bills = self.all_bills[['Number', 'id']].dropna()
        self.list_of_bills = self.bills['Number'].to_list()
        self.bill_ids = self.bills.set_index('Number').to_dict()['id']  
        
        
        
    def check_info(self, bill):
        bill = str(bill)
        q = self.all_bills.set_index('Number').copy()
        q.fillna('', inplace = True)
        resume = q.loc[q.index == bill, 'resume'][bill]
        try:
            if resume == '':
                return 'Знайдено картку законопроекту, проте *коментар відсутній*'
            else:
                return resume
        except:
            return f'В базі знайдено більше одного законопроекту з номером {bill}. Видаліть непотрібний'
        
 

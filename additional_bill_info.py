import requests
from bs4 import BeautifulSoup as bs

""" 
Задача модуля - определить главный комитет законопроекта по ссылке на страницу законопроекта и хронологию рассмотрения. Используется библиотекой Answer для формирования части ответа.

"""

class billProject():
    def __init__(self, link):

        # список того что нас интересует
        my_list = ['Номер, дата реєстрації:', 'Редакція законопроекту:','Рубрика законопроекту:', "Суб'єкт права законодавчої ініціативи:",
                'Головний комітет:', 'Ініціатор(и) законопроекту:']

        # центральное табло інформации сайта рада
        r = requests.get(link)
        soup = bs(r.text, 'html.parser')
        tables = soup.find_all('table')
        info = soup.find_all('div', attrs={'class':'zp-info'})

        # dt - список слева, по которому ми будем гонять наш ліст,  dd - справа, со значеніямі


        dt = info[0].contents[1].find_all('dt')
        dd = info[0].contents[1].find_all('dd')

        # так как последовательность на сайте меняется в завісімості от прохожденія законопроекта
        # ми форміруем спісок всех позіцій, а потом іщем его індекс

        dts = []
        for i in dt:
            dts.append(i.text)
            
            
        try:
            main_committee = f'{dd[dts.index(my_list[4])].text.split("Комітет")[1]}'
        except:
            main_committee = ''

        subject = dd[dts.index(my_list[3])].text

        deps = []
        for i in dd[dts.index(my_list[5])].find_all('li'):
            deps.append(i.text.split(' (')[0])
            
        chronology = tables[0]

        tr = chronology.find_all('tr')
        date = tr[1].contents[1].text
        status = tr[1].contents[3].text

        self.chronology = f'⏱ Остання дія: *{date}* {status}'
        self.committee = f' 👑 *Головний комітет*: {main_committee}'

    
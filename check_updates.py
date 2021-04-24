import requests
from bs4 import BeautifulSoup as bs
from analizator import Analizator
from methods_analizator import AnalizatorMethod
import ninox_log as nl
from time import sleep

class CheckNewBills(AnalizatorMethod):

    def __init__(self):

        link = self.make_concat_search_link()

        soup = self.make_soup(link)

        self.tr = soup.find_all('tr')

    def check_tags_in_names(self):

        links = []
        no_tags = 0
        with_tags =0
        for i in range(1, len(self.tr)):
            my_dict = self.make_dict_from_name(self.tr, i)
            if len(my_dict['tags']) == 0:
                no_tags+=1
            else:
                with_tags+=1
            links.append(my_dict)
            print(f'links -> {len(links)}')
            print(f'names with no tags -> {no_tags}')
            print(f'names with tags -> {with_tags}')

        return links


    def check_links(self, links):
        
        self.to_check = []
        self.no_tags = []
        self.with_tags = []
        self.pdf = []
        self.exception_links = []

        e=1
        print(f'len links = {len(links)}')
        for i in links:
            try:
                if e % 10 ==0:
                    sleep(2)
                a = Analizator(i['link'])
                if a.status == 'no_file':
                    self.to_check.append(i)
                elif a.status == 'pdf' or a.status == 'rtf':
                    self.pdf.append(i)
                elif a.status == 'ok':
                    if len(a.result) == 0:
                        self.no_tags.append(i)
                    else:
                        q = {'link': i, 'tags':a.result}
                        self.with_tags.append(q)
                else:
                    pass
                e+=1
            except Exception as ex:
                print(ex)
                print(e)
                self.exception_links.append(i)
                e+=1
        if len(self.pdf)>0:
            print(nl.send_file_to_check(self.pdf))




        print(f'need_to_check -> {len(self.to_check)}')
        print(f'with no tags -> {len(self.no_tags)}')
        print(f'with tags -> {len(self.with_tags)}')
        print(f'pdf -> {len(self.pdf)}')
        print(f'exceptions -> {len(self.exception_links)}')

    def check_everything(self):
        links = self.check_tags_in_names()
        self.check_links(links)
        message = f'''need_to_check -> {len(self.to_check)}
with no tags -> {len(self.no_tags)}
with tags -> {len(self.with_tags)}
pdf -> {len(self.pdf)}'''
        return message

    
        



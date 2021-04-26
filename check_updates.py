import requests
from bs4 import BeautifulSoup as bs
from analizator import Analizator
from methods_analizator import AnalizatorMethod
import ninox_log as nl
from time import sleep

class CheckNewBills(AnalizatorMethod):

    def __init__(self, yesterday = False):
        self.yesterday = yesterday
        link = self.make_concat_search_link(yesterday = self.yesterday)

        soup = self.make_soup(link)

        self.tr = soup.find_all('tr')

    def check_tags_in_names(self):

        links = []
        self.find_tag_in_name = []
        no_tags = 0
        with_tags =0
        for i in range(1, len(self.tr)):
            my_dict = self.make_dict_from_name(self.tr, i)
            if len(my_dict['tags']) == 0:
                no_tags+=1
            else:
                with_tags+=1
                self.find_tag_in_name.append(my_dict)
            links.append(my_dict)
        print(f'links -> {len(links)}')
        print(f'names with no tags -> {no_tags}')
        print(f'names with tags -> {with_tags}')

        return links


    def check_links(self, links, rtrn = False):
        
        self.to_check = []
        self.no_tags = []
        self.with_tags = []
        self.exception_links = []

        print(f'len links = {len(links)}')
        for i in links:
            try:
                sleep(1)
                a = Analizator(i['link'])
                if a.status == 'no_file':
                    self.to_check.append(i)
                elif a.status == 'ok':
                    if len(a.result) == 0:
                        self.no_tags.append(i)
                    else:
                        i['tags'] = a.result
                        self.with_tags.append(i)
                else:
                    pass
            except Exception as ex:
                print(ex)
                self.exception_links.append(i)



        print(f'need_to_check -> {len(self.to_check)}')
        print(f'with no tags -> {len(self.no_tags)}')
        print(f'with tags -> {len(self.with_tags)}')
        print(f'exceptions -> {len(self.exception_links)}')
        if rtrn:
            return self.to_check, self.no_tags, self.with_tags, self.exception_links

    def check_everything(self):
        links = self.check_tags_in_names()
        self.check_links(links)
        message = f'''need_to_check -> {len(self.to_check)}
with no tags -> {len(self.no_tags)}
with tags -> {len(self.with_tags)}'''
        return message

    
        



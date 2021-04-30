import requests
from bs4 import BeautifulSoup as bs
from methods_analizator import AnalizatorMethod
from parsing_process import Parse

"""
Задача модуля последовательно запустить методы родительского класса и
определить наличие файла на странице законопроекта, конвертировать его 
в текст и прогнать на наличие тэгов. Выдает СТАТУС и СПИСОК НАЙДЕННЫХ ТЭГОВ.
"""

class Analizator(AnalizatorMethod):
    
    def __init__(self, link):
        soup = self.make_soup(link)
        try:
            file_link = self.check_if_file_exist(soup)
            self.file_link = file_link
            if self.file_link != '':
                self.status = 'ok'
                text = Parse().download_file(self.file_link)
                self.result = self.find_tags(text)
            else:               
                self.status = 'no_file'  
        except:
            self.status = 'error'

            
        



       
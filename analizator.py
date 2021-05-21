from methods_analizator import AnalizatorMethod
from parsing_process import Parse


"""
Задача модуля последовательно запустить методы родительского класса и
определить наличие файла на странице законопроекта, конвертировать его 
в текст и прогнать на наличие тэгов. Выдает СТАТУС и СПИСОК НАЙДЕННЫХ ТЭГОВ.
"""

class Analizator(AnalizatorMethod):
    def __init__(self, link, tags):
        print(1)
        soup = self.make_soup(link)
        print(2)
        self.tags = tags
        print(3)
        try:
            print(4)
            file_link = self.check_if_file_exist(soup)
            print(5)
            self.file_link = file_link
            print(6)
            if self.file_link != '':
                print(7)
                self.status = 'ok'
                print(8)
                text = Parse().download_file(self.file_link)
                print(9)
                self.result = self.find_tags(text)
                print(10)
                self.texts = text
                print(35)
            else:
                print(11)  
                self.status = 'no_file'  
                print(12)
                print(self.status) 
                print(13)
                self.result = ''
                print(14)
        except:
            print(15)
            self.status = 'error'
            print(16)
            print(self.status) 
            self.result = ''
            print(17)

            
        



       
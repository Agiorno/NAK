import requests
from bs4 import BeautifulSoup as bs
from methods_analizator import AnalizatorMethod


class Analizator(AnalizatorMethod):
    
    def __init__(self, link):

        soup = self.make_soup(link)
       
        try:
            file_link = self.check_if_file_exist(soup)
            self.file_link = file_link
            
            if file_link != '':
                the_file = requests.get(file_link, stream=True)
                extension = self.get_extension(the_file)

                if extension == 'docx' or extension =='doc':
                    self.status = 'ok'
                    self.result = self.docx_analize(the_file)
                
                elif extension == 'rtf':
                    self.status = 'rtf'
                
                elif extension == 'pdf':
                    self.status = 'pdf'
                else:
                    self.status = 'wrong extension'
            else:
                self.status = 'no_file'   
        except:
            self.status = 'error'
        



       
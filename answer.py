import os
from analizator import Analizator, get_links, get_atrrs
       

class Answer():
    
    def __init__(self, link):
        self.answer = Analizator(link, 'tags')
        self.law_number = get_atrrs(link)[1]
        self.law_name = get_atrrs(link)[0]
        self.info_message = info_message = f'''✏️ *Назва*: {self.law_name}
        
📑 *Номер*:  🔗[{self.law_number}]({link})'''
        
        if self.answer.status == 'ok':
            
            self.my_message = self.docx_answer()
            os.remove('text.docx')

        elif self.answer.status == 'error':
            self.my_message = self.docx_answer()
            
        elif self.answer.status == 'rtf':
            self.my_message = self.rtf_answer()
            
            
        elif self.answer.status == 'pdf':
            self.my_message = self.pdf_answer()

        else:
            self.my_message = self.wrong_format_answer()
            
    def docx_answer(self):
        if len(self.answer.result)==0:
            my_message = f"""{self.info_message} 
*Аналіз тегів*: ✅ У законопроекті відсутні ключові слова"""

        else:
            my_message = f"""{self.info_message} 
*Аналіз тегів*: ❗️❗️❗️  У законопроекті знайдені ключові слова: """
            for i in self.answer.result:
                my_message = f'{my_message}{i} '
        
        return my_message
    
    def error_answer(self):
        
        my_message = f"""{self.info_message} 
*Аналіз тегів*: 🚫 У законопроекті відсутній текст для аналізу"""
        
        return my_message
    
    def rtf_answer(self):
        
        my_message = f"""{self.info_message} 
*Аналіз тегів*: ❌ Знайдено текст, проте бот _не може_ аналізувати .rtf файли. [Передивіться особисто.]({self.answer.file_link})"""
        
        return my_message
    
    def pdf_answer(self):
        
        my_message = f"""{self.info_message} 
*Аналіз тегів*: ❌ Знайдено текст, проте бот _не може_ аналізувати .pdf файли. [Передивіться особисто.]({self.answer.file_link})"""
        
        return my_message
    
    def wrong_format_answer(self):
        
        my_message = f"""{self.info_message} 
*Аналіз тегів*: ❌ Неможливо опрацювати текст законопроекту. [Перевірте особисто]({self.answer.file_link})"""
        
        return my_message
from analizator import Analizator
from additional_bill_info import billProject
from methods_analizator import AnalizatorMethod as am
       

class AnswerMethod:

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

    def no_file(self):
        
        my_message = f"""{self.info_message} 
*Аналіз тегів*: ❌ Текст законопроекту відсутній. Ми щогодини оновлюємо інформацію та повідомимо вас, після аналізу тексту, якщо в ньому будуть знайдені ключові слова."""
        
        return my_message



class Answer(AnswerMethod):
   
    def __init__(self, link):
        self.answer = Analizator(link)
        self.law_name, self.law_number = am().get_atrrs(link)
        self.info_message = info_message = f'''📑 *Номер*:  🔗[{self.law_number}]({link})
        
✏️ *Назва*: {self.law_name}
'''
        
        if self.answer.status == 'ok':
            
            self.my_message = self.docx_answer()
           

        elif self.answer.status == 'error':
            self.my_message = self.docx_answer()
            
        elif self.answer.status == 'rtf':
            self.my_message = self.rtf_answer()
            
            
        elif self.answer.status == 'pdf':
            self.my_message = self.pdf_answer()
        
        elif self.answer.status == 'no_file':
            self.my_message = self.no_file()

        else:
            self.my_message = self.wrong_format_answer()

        self.my_message = f'''{self.my_message}

{billProject(link).chronology}

{billProject(link).committee}'''
            
    
    
    
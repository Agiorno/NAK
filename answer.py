from analizator import Analizator
from additional_bill_info import billProject
from methods_analizator import AnalizatorMethod as am
import json

"""
Задача метода - сформировать обратный ответ на запрос проекта НАК на основе АНАЛИЗАТОРА ТЕКСТА

"""

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
    
    def wrong_format_answer(self):
        
        my_message = f"""{self.info_message} 
*Аналіз тегів*: ❌ Неможливо опрацювати текст законопроекту. [Перевірте особисто]({self.answer.file_link})"""
        
        return my_message

    def no_file(self):
        
        my_message = f"""{self.info_message} 
*Аналіз тегів*: ❌ Текст законопроекту відсутній. Ми щогодини оновлюємо інформацію та повідомимо вас, після аналізу тексту, якщо в ньому будуть знайдені ключові слова."""
        
        return my_message
    
    def wrong_request(self):
        my_message = 'НЕКОРЕКТНИЙ ЗАПИТ'
        
        return my_message
    
    def make_inline_keyboard(self, empty=False, **kwargs):
        if empty:
            kb = json.dumps({ "inline_keyboard":[[]]})
        else:
            dogs = []
            for arg in kwargs.values():
                dogs.append(arg)
            fa = []
            fa.append(dogs)
            ik = { "inline_keyboard":fa}
            kb = json.dumps(ik)
        return kb



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
        
        elif self.answer.status == 'no_file':
            self.my_message = self.no_file()

        else:
            self.my_message = self.wrong_format_answer()

        self.my_message = f'''{self.my_message}

{billProject(link).chronology}

{billProject(link).committee}'''
            
    
    
    
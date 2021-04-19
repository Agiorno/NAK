from ninox_log import send_log
from upload_bills import get_links, send_info, Bills
import json  
from answer import Answer
from bothandler import BotHandler

class NAK(BotHandler):
    
    BOT_URL = None
    
    def __init__(self, data):
        self.data = data
        self.handle_data()

    def generate_keyboard(self, bill, my_answer):
            if str(self.message) in bill.list_of_bills:
                self.text = bill.check_info(str(self.message))
                self.kb = json.dumps({ "inline_keyboard":[[]]})
            else:
                self.text = "Цей законопроект відсутній в базі" 



                self.kb=json.dumps(
                    { "inline_keyboard":
                        [
                            [
                                { "text": "Додати", "callback_data": "1" },
                                { "text": "Не додавати", "callback_data": "2" }
                                # { "text": "Автори", "callback_data": "3" }

                            ]
                        ]
                    }
                )
            my_message = f'''{my_answer}

📍 *CRM*: {self.text}''' 

            return my_message

    def get_url(self):
        url = ''
        for i in self.data['callback_query']['message']['entities']:
            if 'url' in i.keys():
                if url == '':
                    url = i['url']
                else:
                    if len(i['url'])<len(url):
                        url = i['url']
        return url

    def prepare_data_for_answer(self, link):

        self.bill = Bills()


        m = Answer(link)
        my_message = m.my_message
        my_message = self.generate_keyboard(self.bill, my_message)  

        send_log(self.data, my_message, m.law_name, m.law_number, link)

        return my_message
    
    
    def prepare_data_for_answer1(self, link):
        answer = self.prepare_data_for_answer(link)
        json_data = {
            "chat_id": self.chat_id,
            "text": answer,
            "reply_to_message_id": self.message_id,
            "parse_mode": 'markdown',
            'reply_markup': self.kb
        }
       

        return json_data
    
    def bot_analize_bills_for_nak(self):

        if  self._type == 'message':
            array = get_links(self.message)

            if len(array)==0:
                self.send_message(self.just_text('НЕКОРЕКТНИЙ ЗАПИТ'))

            else:

                for i in array:

                    answer_data = self.prepare_data_for_answer1(i)
                    self.send_message(answer_data)
                    print('message has sent')



        else:
            try:

                if self.message == "1":
                    url = self.get_url()
                    send_info(url)
                    self.send_message(self.just_text('Законопроект доданий до CRM в розділ *Bills* (Постійний моніторинг).'))
                    self.bill = Bills()

                else:
                    self.send_message(self.just_text('Законопроект не включений до постійного моніторінгу'))

                self.edit_reply()
                print('keyboard has removed')
                self.bill = Bills()
            
            except KeyError:

                 self.send_message(self.just_text('НЕКОРЕКТНИЙ ЗАПИТ'))
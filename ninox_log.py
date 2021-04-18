import ast
import requests
from ninox import Ninox


with open("monkey", "r") as f:
    password = ast.literal_eval(f.read())
try:
    n = Ninox(password['Anton'], )
    n.team = n.get_team()['NAK']
    n.database = n.get_database()['BOT']
    my_schema = n.schema()
except:
    n = Ninox(password['Nadin'], )
    n.team = n.get_team()['NAK']
    n.database = n.get_database()['BOT']
    my_schema = n.schema()
    
def send_log(data, answer, law_name, law_number, link):
    message = data['message']['text']
    chat_id = data['message']['chat']['id']
    try:
        first_name = data['message']['chat']['first_name']
    except:
        first_name = ''
        
    try:
        last_name = data['message']['chat']['last_name']
    except:
        last_name = ''
    try:
        username = data['message']['chat']['username']
    except:
        username = ''
    dogs = []
    di = {'fields':{'message': str(message), 'chat_id': str(chat_id), 'first_name':str(first_name), 'last_name':str(last_name), 'user_name':str(username), 'answer':answer,'law_name':law_name, 'law_number':law_number, 'URL':link}}
    dogs.append(di)
    
    result = n.send_to_ninox(dogs, my_schema['log'])
    
    return result


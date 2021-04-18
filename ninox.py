import requests
import pandas as pd
import json
import ast

class Ninox():
    
    def __init__(self, bearer):
        self.bearer = bearer
        self.ninox_headers = {'Content-Type': 'application/json',
               'Authorization': self.bearer}
    
    def schema(self):
        url = 'https://api.ninoxdb.de/v1/teams/%s/databases/%s/tables/?perPage=10000' % (
            self.team, self.database)
        response = requests.request("GET", url, headers=self.ninox_headers)
        a = response.json()
        b = pd.json_normalize(a)
        schem = b.set_index('name').to_dict('dict')['id']
        return schem

    def send_to_ninox(self, array, table):
        url = 'https://api.ninoxdb.de/v1/teams/%s/databases/%s/tables/%s/records/' % (self.team, self.database, table)
        payload = json.dumps(array)
        response = requests.request(
            "POST", url, headers=self.ninox_headers, data=payload.encode('utf-8'))
        return response

#     def get_from_ninox(self, table, json=False, page=None, filters=None):
#         url = 'https://api.ninoxdb.de/v1/teams/%s/databases/%s/tables/%s/records/?perPage=10000' % (self.team, self.database, table)
#         response = requests.request("GET", url, headers=self.ninox_headers)
#         a = response.json()
#         b = pd.json_normalize(a)
#         b.drop(['sequence', 'createdAt', 'createdBy', 'modifiedAt', 'modifiedBy'], 1, inplace=True)
#         cols = []
#         for i in b.columns.to_list():
#             cols.append(i.replace('fields.','').strip())
#         b.columns = cols
#         if json == False:
#             result = b
#         else:
#             result = a
#         return result
    
    
    def get_from_ninox(self, table, json=False,custom_url = None, page=None):
        if page:
            pg = f'page={page}&'
        else:
            pg= ''
        url = 'https://api.ninoxdb.de/v1/teams/%s/databases/%s/tables/%s/records?perPage=10000' % (self.team, self.database, table)
        if custom_url:
            url = custom_url
        response = requests.request("GET", url, headers=self.ninox_headers)
        a = response.json()
        if json == False:
            b = pd.json_normalize(a)
            b.drop(['sequence', 'createdAt', 'createdBy', 'modifiedAt', 'modifiedBy'], 1, inplace=True)
            cols = []
            for i in b.columns.to_list():
                cols.append(i.replace('fields.','').strip())
            b.columns = cols
            result = b
        else:
            result = a
        return result

    def get_team(self):
        
        url = 'https://api.ninoxdb.de/v1/teams/'
        response = requests.request("GET", url, headers=self.ninox_headers)
        a = response.json()
        b = pd.json_normalize(a)
        schem = b.set_index('name').to_dict('dict')['id']
        return schem
    
    def get_database(self):
        url = 'https://api.ninoxdb.de/v1/teams/%s/databases/' % (
            self.team)
        response = requests.request("GET", url, headers=self.ninox_headers)
        a = response.json()
        b = pd.json_normalize(a)
        schem = b.set_index('name').to_dict('dict')['id']
        return schem

    def odd(self, num):
        if (num % 2) == 0:
            a = 0
        else:
            a = 1
        return a
    def used_links(self):
        return self.get_from_ninox(self.schema()['Voting'])['URL_votes'].dropna().to_list()
#!/usr/bin/python3

import requests
from time import sleep
import json


with open('./mock_users.csv', mode='r') as f:
    for line in f:
        data = line.replace('\n', '').split(',')
        p_data = {
                'email': data[0],
                'first_name': data[1],
                'last_name': data[2],
                'cel': data[3],
                'tel': data[4],
                'doc_type': data[5],
                'doc_number': data[6],
                'city': data[7],
                'password': data[8]
                }
        r = requests.post('http://127.0.0.1:8000/signin',
                data=json.dumps(p_data),
                headers={'Content-Type': 'application/json'})
        if r.status_code != 200:
            print(r.content)

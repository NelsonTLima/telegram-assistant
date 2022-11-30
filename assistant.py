import requests, json, threading, os
from dotenv import load_dotenv
load_dotenv()

updates = []
__token = os.environ['TELEGRAM_TOKEN']
__chat_id  = os.environ['MY_CHAT_ID']

def send(message):
    data = {"chat_id": __chat_id, "text": message}
    __url = f'https://api.telegram.org/bot{__token}/sendMessage'
    requests.post(__url, data)

def get_updates():
    data = {"offset": -1, "limit": 1, "allowed_updates": ["message"]}
    __url = f'https://api.telegram.org/bot{__token}/getUpdates'
    request = requests.get(__url, data)
    update = request.json()['result'][0]
    update_id = update['update_id']
    message = update['message']['text']

    return message, update_id

def get_chat_info():
    data = {"offset": -1, "limit": 1, "allowed_updates": ["message"]}
    __url = f'https://api.telegram.org/bot{__token}/getUpdates'
    return requests.get(__url, data).json()

def get_chat_id():
    return chat_info()['result'][0]['message']['from']['id']

def listen():
    last_message, last_update_id = get_updates()
    update_id = last_update_id
    while update_id == last_update_id:
        chat_request, update_id = get_updates()
        if update_id != last_update_id:
            return chat_request

if __name__ == '__main__':

    while True:
        chat_request = listen()
        if chat_request == 'ip' or chat_request == 'Ip' or chat_request == 'IP':
            send(requests.get('http://ifconfig.me').text)

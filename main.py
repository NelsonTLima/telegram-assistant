import requests, json, os, hashlib
from dotenv import load_dotenv
load_dotenv()

telegram_token = os.environ['TELEGRAM_TOKEN']
admin_id  = os.environ['MY_CHAT_ID']
stored_password = os.environ['PASSWORD']

def sha256_hash(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

def require_password():
    send('Password is required:')
    provided_password, chat_id = listen()
    return sha256_hash(provided_password) == stored_password

def read_json():
    with open('userData.json') as file:
        return json.load(file)

def write_json(user_data):
    with open('userData.json', 'w') as file:
        file.write(json.dumps(user_data, indent=4))

def read_notes(user_data):
    try:
        notes = user_data["notes"]
    except:
        user_data["notes"] = []
        notes = user_data["notes"]
    return notes

def avoid_unfinished_words(text):
    text_array = text.split(' ')
    if len(text_array) > 1:
        new_array = []
        for i in range(len(text_array)-1):
            new_array.append(' ' + text_array[i])
        text = ''
        text = text.join(new_array)
    return text


def get_telegram_update():
    data = {"offset": -1, "limit": 1, "allowed_updates": ["message"]}
    url = f'https://api.telegram.org/bot{telegram_token}/getUpdates'
    request = requests.get(url, data)
    update = request.json()['result'][0]
    update_id = update['update_id']
    message = update['message']['text']
    chat_id = update['message']['from']['id']

    return message, update_id, chat_id

def listen():
    last_message, last_update_id, last_chat_id = get_telegram_update()
    update_id = last_update_id
    while update_id == last_update_id:
        chat_request, update_id, chat_id = get_telegram_update()
    return chat_request, chat_id

def send(message):
    data = {"chat_id": chat_id, "text": message}
    url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    requests.post(url, data)

def take_note():
    send('Ok. 📝')
    note, chat_id = listen()
    if note.lower() != 'abort':
        try:
            user_data = read_json()
            notes = read_notes(user_data)
        except:
            notes = []
            user_data = {"notes" : notes}
        notes.append(note)
        write_json(user_data)
        send('Done.')

def show_all_notes():
    try:
        user_data = read_json()
        notes = read_notes(user_data)
        index = 1
        for note in notes:
            if len(note) <= 24:
                send(f'{index} - ' + note)
            else:
                send(f'{index} - ' + avoid_unfinished_words(note[:24]) + '[...]')
            index +=1
        if len(notes) == 0:
            send("There's any note registered!")
    except:
        send("There's any note registered!")

def show_specific_note(index):
    try:
        user_data = read_json()
        note = read_notes(user_data)[index]
        send('"'+ note + '"')
    except:
        send("I couldn't find that note.")

def clear_all_notes():
    try:
        user_data = read_json()
        user_data["notes"] = []
        write_json(user_data)
        send('Notes were cleared.')
    except:
        send("I couldn't clear the notes.")

def get_note_index(chat_request):
    note_index = None
    try:
        note_index = int(chat_request[9:]) - 1
    except:
        send('Wich one?')
        while note_index == None:
            try:
                index, chat_id = listen()
                note_index = int(index) - 1
            except:
                send('A valid index number is needed.')
    return note_index

def send_ip():
    ip = None
    while ip == None:
        ip = requests.get('https://ifconfig.me').text
    if str(chat_id) == str(admin_id):
        send(ip)
    else:
        password_check = require_password()
        if password_check == True:
            send(ip)

def process_commands(chat_request):
    match chat_request:
        case 'ip':
            send("Here's my ip:")
            send_ip()
        case 'chat id':
            send("Here's our chat id:")
            send(chat_id)
        case 'take note':
            take_note()
        case 'show all notes':
            show_all_notes()
        case 'clear all notes':
            clear_all_notes()
    if chat_request[:9] == 'show note':
        note_index = get_note_index(chat_request)
        show_specific_note(note_index)

def main():
    while True:
        global chat_id
        try:
            chat_request, chat_id = listen()
            process_commands(chat_request.lower())
        except: pass

if __name__ == '__main__':
    main()

import requests, json, os, hashlib, traceback
from dotenv import load_dotenv
load_dotenv()

# Global variables:
telegram_token = os.environ['TELEGRAM_TOKEN']
admin_id  = os.environ['MY_CHAT_ID']
stored_password = os.environ['PASSWORD']

# HELP FUNCTIONS:

def sha256_hash(string):
    '''
    Produces a Sha-256 hash.

    args:
    - string (str): the string to be  hashed.

    returns:
    - hash (str): the sha256 hash.
    '''
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

def compare_password(provided_password, stored_hash):
    '''
    Compares if a password hash is equal to the the stored one.

    args:
    - provided_password (str): the un-hashed string with the password the user has provided.
    - stored_hash (str): the hashed password to compare.

    returns:
    - (bool): True if the passwords are equal and False if it's not equal.
    '''
    return sha256_hash(provided_password) == stored_hash

def is_admin(chat_id):
    '''
    Checks if the chat id is the same chat id the admin is currently using.

    Args:
    - chat_id (string or int) : the chat id.

    Returns:
    - (bool): True if the ids are equal and False if it's not equal.
   '''
    return str(chat_id) == str(admin_id)

def remove_incomplete_words(string):
    '''
    Returns the same string, but avoids finish with an incomplete word by deleting the last word.

    Arg:
    - string (str): the original string.

    Returns:
    - string (str) : if it's only one word returns itself, otherwise removes last word.
    '''
    string_array = string.split(' ')
    if len(string_array) > 1:
        new_array = []
        for i in range(len(string_array)-1):
            new_array.append(' ')
            new_array.append(string_array[i])
        new_array.pop(0)
        string = ''
        string = string.join(new_array)
    return string

def get_index_from_command(command):
    '''
    Finds out the index of from the user command.

    args:
    - command (string) : a string with "some text + a number" is expected.

    returns:
    - note_index (int) : the int number in the end of the phrase.

    Case there's not a valid number in the end of the command string, this function returns a NoneType.
    '''
    last_word = command.split(' ')[-1]
    try:
        index = int(last_word) - 1
    except:
        index = None
    return index

def return_chat_id_and_message(update):
    '''
    Gets the treated telegram udate and returns the chat id and the message.

    args:
    - update (dictionaire) : a dictionaire with an update from telegram.

    Returns:
    - chat id (string) : the id of the message's source.
    - message (string) : the message itself.
    '''
    return update['chat_id'], update['message']

# WRITE AND READ JSON FUNCTIONS:

def write_to_json(user_data):
    '''
    writes a json file containing a dictionaire with the user data.

    args:
    - user_data (dict): An object containing the data to be writen.
    '''
    with open('userData.json', 'w') as file:
        file.write(json.dumps(user_data, indent=4))

def read_from_json():
    '''
    Tries to read user's json file. In case of faliure, it creates the file with an empty dictionaire.

    returns:
    - initialized_user_data (dict): An dictionaire containing the data in the file.
    '''
    try:
        with open('userData.json') as file:
            user_data = json.load(file)
    except:
        user_data = {}
        write_to_json(user_data)
    return user_data

def read_or_initialize_notes():
    '''
    Tries to get the user's notes. In case of faliure, it creates the note key with an empty array.

    returns:
    - notes (list) : An array containing the user's notes.
    '''
    user_data = read_from_json()
    try:
        notes = user_data["notes"]
    except:
        user_data["notes"] = []
        write_to_json(user_data)
        notes = user_data["notes"]
    return notes

# "It's better to ask forgiveness than permission". That's why i chose a try-except
# statement in the last 2 functions instead of checking if the file exists.

def write_note(note):
    '''
    The whole process of writing a note to the json file.

    args
    - note (str) : the note to be writen.
    '''
    notes = read_or_initialize_notes()
    user_data = read_from_json()
    notes.append(note)
    user_data['notes'] = notes
    write_to_json(user_data)

def delete_note(note):
    '''
    The whole process of deleting a note to the json file.

    args
    - note (str) : the note to be removed.
    '''
    notes = read_or_initialize_notes()
    user_data = read_from_json()
    notes.remove(note)
    user_data['notes'] = notes
    write_to_json(user_data)

def clear_all_notes():
    '''
    removes all notes from the json file.
    '''
    user_data = read_from_json()
    user_data["notes"] = []
    write_to_json(user_data)

def get_ip():
    '''
    Gets the server's public IP from 'ifconfig.me' and returns it.
    '''
    ip = None
    while ip == None:
        ip = requests.get('https://ifconfig.me').text
    return ip

# FUNCTIONS THAT INTERACT WITH TELEGRAM'S API:

def get_telegram_update():
    '''
    Gets an update from telegram's API.

    returns:
    A dictionaire containing the update id, the chat id and the message.
    '''
    data = {"offset": -1, "limit": 1, "allowed_updates": ["message"]}
    url = f'https://api.telegram.org/bot{telegram_token}/getUpdates'
    update = requests.get(url, data).json()['result']

    if isinstance(update, list) == True and update != []:
        update = update[0]
        dictionaire = {
                "id" : update['update_id'],
                "message" : update['message']['text'],
                "chat_id" : update['message']['from']['id']
                }
    else:
        dictionaire = {
                "id" : None,
                "message": None,
                "chat_id": None
                }
    return dictionaire

# SEND FUNCTIONS.

def send(message, chat_id):
    '''
    Sends a message to the user.

    args:

    - message (string) : message to be sent.
    - chat_id (string) : Destination of the message. Default is the admin.

    Returns:
    The API Response.
    '''
    data = {"chat_id": chat_id, "text": message}
    url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    return requests.post(url, data)

def send_enumerated_notes(notes, chat_id):
    '''
    Check if it has notes. If check is true, sends all notes' beginnings and its indexes to the user.
    Otherwise, sends a message telling tha there's any note to send.

    Args:
    - notes (list): a list containing all notes registered.
    - chat_id (string): user's chat'id.

    Returns:
    - Bool: True if has notes and False if it has not.
    '''
    if notes == []:
        send('There is any note to send.', chat_id)
        return False

    for i, note in enumerate(notes, start = 1):
        if len(note) <= 24:
            send(f'{i} - ' + note, chat_id)
        else:
            send(f'{i} - ' + remove_incomplete_words(note[:24]) + '[...]', chat_id)
    return True

# FUNCTIONS THAT HAS TO LISTEN.

def listen():
    '''
    An event listener set to catch telegram's latest update and returning it.

    returns
    - latest update (dict)
    '''
    previous_update = get_telegram_update()
    latest_update = previous_update
    while latest_update == previous_update:
        latest_update = get_telegram_update()
    return latest_update

def require_password(chat_id):
    '''
    Requires a password from the user.

    Args:
    - chat_id (string) : The id from the user's chat.

    Returns:
    - provided_password (string) : the password provided by the user.
    '''
    send('Password is required:', chat_id)
    requeree_id = chat_id
    while chat_id != requeree_id:
        telegram_update = listen()
        chat_id, provided_password = return_chat_id_and_message(telegram_update)
    return provided_password

def send_ip(chat_id):
    '''
    The entire process of sending the ip to the user. But only the admin has free access.

    Args:
    - chat_id (string) : The id from the user's chat.
    '''
    ip = get_ip()
    if is_admin(chat_id) == False:
        password_check = require_password()
        if password_check == True:
            send("Here's my ip:", chat_id)
            send(ip, chat_id)
        else:
            send('Wrong password!')
    send("Here's my ip:", chat_id)
    send(ip, chat_id)
    return True

def take_note(chat_id):
    '''
    The whole process of taking a note and recording it.

    Args:
    - chat_id (string) : The id from the user's chat.
    '''
    send('Ok. 📝', chat_id)
    note = listen()['message']
    if note.lower() != 'abort':
        write_note(note)
        send('Done.', chat_id)

def require_index_number(chat_id):
    '''
    The whole process of requiring an index number.

    args:
    - chat_id (string): user's chat id.
    '''
    note_index = None
    while note_index == None:
        send('A valid index number is needed:', chat_id)
        try:
            index = listen()['message']
            note_index = int(index) - 1
        except:
            note_index = None
    return note_index

def send_specific_note(command, notes, chat_id):
    '''
    The entire process of sending a specific note to the user.

    args:
    - command (string): the command sent by the user to send specific note
    - notes (list): the list of notes registered.
    - chat_id (string): the user's chat id.
    '''
    note_index = get_index_from_command(command)
    while note_index == None or note_index >= len(notes):
        send(f"The total amount of notes is: {len(notes)}", chat_id)
        note_index = require_index_number(chat_id)
    note = '"' + notes[note_index] + '"'
    send(note, chat_id)

def remove_specific_note(command, notes, chat_id):
    '''
    The entire process of removing a specific note to the user.

    args:
    - command (string): the command sent by the user to send specific note
    - notes (list): the list of notes registered.
    - chat_id (string): the user's chat id.
    '''
    note_index = get_index_from_command(command)
    while note_index == None or note_index >= len(notes):
        send(f"The total amount of notes is: {len(notes)}", chat_id)
        note_index = require_index_number(chat_id)
    note = notes[note_index]
    delete_note(note)
    send('Note removed.', chat_id)

# CORE FUNCTIONS:

def process_commands(command, chat_id):
    '''
    The core function that processes all the commands.

    args:
    - comommand (string): the command sent by the user.
    - chat_id (string): user's chat id.
    '''
    notes = read_or_initialize_notes()
    match command:
        case 'ip':
            send_ip(chat_id)
        case 'chat id':
            send("Here's our chat id:", chat_id)
            send(chat_id, chat_id)
        case 'take note':
            take_note(chat_id)
        case 'show all notes':
            send_enumerated_notes(notes, chat_id)
        case 'clear all notes':
            if notes == []:
                send("There is any note to remove.", chat_id)
            else:
                clear_all_notes()
                send('Notes cleared!', chat_id)
    if command[:9] == 'show note':
        if notes == []:
            send('There is any note to send.', chat_id)
        else:
            send_specific_note(command, notes, chat_id)
    elif command[:11] == 'remove note':
        if notes == []:
            send('There is any note to remove.', chat_id)
        else:
            remove_specific_note(command, notes, chat_id)

def main():
    while True:
        try:
            telegram_update = listen()
            chat_id, command  = return_chat_id_and_message(telegram_update)
            process_commands(command.lower(), chat_id)
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()

if __name__ == '__main__':
    main()

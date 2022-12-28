from main import *
load_dotenv()
admin_id  = os.environ['MY_CHAT_ID']

def test_sha256_hash():
    # Test the sha256_hash function to ensure it correctly produces a Sha-256 hash of a given string.
    assert sha256_hash('hello world') == 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
    assert sha256_hash('password') != 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'

def test_compare_password():
    # Tests if the function is correctly returning the right boolean.
    # True if the password correspond to the hash and false if it doesn't.
    assert compare_password('test1234', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244') == True
    assert compare_password('1234', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244') == False

def test_is_admin():
    # Tests if the function is correctly returning the right boolean.
    # True if the string correspond to the admin's id and false if it doesn't.
    assert is_admin(admin_id) == True
    assert is_admin('197665123') == False

def test_remove_incomplete_words():
    # Test the remove_incomplete_words function to ensure it returns the original string without the last word.
    # If the original string has only one word. The word is expected.
    assert remove_incomplete_words('hello, beautiful worl') == 'hello, beautiful'
    assert remove_incomplete_words('hello') == 'hello'
    assert remove_incomplete_words('') == ''
    assert remove_incomplete_words(' ') == ''
    assert remove_incomplete_words(',') == ','

def test_get_index_from_command():
    # Test get_index_from_command to ensure it returns the number at the end of the string.
    # If there's any number, a NoneType is expected as a return.
    assert get_index_from_command('show note 5') == 4
    assert get_index_from_command('show note') == None
    assert get_index_from_command('show note x') == None

def test_return_chat_id_and_message():
    # Test return_chat_id_and_message to ensure it correctly returns the chat id and the message from the update dictionaire.
    update = {
            "id" : "fake_id",
            "message" : "fake_message",
            "chat_id" : 'fake_chat_id'
            }
    assert return_chat_id_and_message(update) == ('fake_chat_id', 'fake_message')

def test_write_to_json():
    # Test write_to_json to ensure it correctly writes the user data to the json file.
    try:
        with open('userData.json') as file:
            user_data = json.load(file)
    except:
        user_data = {}
    write_to_json(user_data)
    assert read_from_json() == user_data

def test_read_from_json():
    # Test read_from_json if it correctly reads the user data from the json file.
    try:
        with open('userData.json') as file:
            user_data = json.load(file)
    except:
        user_data = {}
    assert read_from_json() == user_data

def test_read_or_initialize_notes():
    # Test read_or_initialize_notes to ensure it correctly reads the note list inside the json file.
    try:
        with open('userData.json') as file:
            user_data = json.load(file)
            notes = user_data['notes']
    except:
        notes = []
    assert read_or_initialize_notes() == notes

def test_write_note():
    # Test to ensure that the write_note function correctly reccords a note in the json file.
    write_note('test note')
    with open('userData.json') as file:
        user_data = json.load(file)
        notes = user_data['notes']
    assert notes[-1] == 'test note'

def test_delete_note():
    # Test to ensure that the delete_note correctly deletes a note from the json file.
    write_note('test 1')
    write_note('test 2')
    delete_note('test 1')
    with open('userData.json') as file:
        user_data = json.load(file)
        notes = user_data['notes']
    statement = 'test 1' in notes
    assert statement == False

def test_clear_all_notes():
    # Test to ensure it removes all notes from the json file.
    clear_all_notes()
    with open('userData.json') as file:
        user_data = json.load(file)
        notes = user_data['notes']
    assert len(notes) == 0

def test_get_ip():
    # Test get_ip to ensure it returns a string suposetely containing an ipv4 number.
    ip = get_ip()
    assert isinstance(ip, str)
    assert len(ip.split('.')) == 4
    for i in ip.split('.'):
        assert isinstance(int(i), int)

def test_get_telegram_update():
    # Test get_telegram_update to ensure it returns an dictionaire with id, message and chat_id keys.
    assert list(get_telegram_update().keys()) == ['id', 'message', 'chat_id']

def test_send():
    # Test send function to ensure it correctly sends a string by checking if the request status is 200,
    # if the telegram confirms with an "ok" and if the text sent was correct.
    request = send('test', admin_id)
    assert request.status_code == 200
    assert request.json()['ok'] == True
    assert request.json()['result']['text'] ==  'test'

def test_send_enumerated_notes():
    # Test send_enumerated_notes by checking if it completes its goals without any exceptions.
    assert send_enumerated_notes([], admin_id) == False
    assert send_enumerated_notes(['testing', 'enumerate', 'notes', 'here is a big string to test this function'], admin_id) == True

def test_send_ip():
    # Test send_ip by checking if the function completes its goal without any exceptions.
    assert send_ip(admin_id) == True

if __name__ == "__main__":
    pass

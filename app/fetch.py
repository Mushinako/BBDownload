import json
import requests

import defconst
import pwd


# Read Personal Data from JSON
def read_personal_data():
    with open('data/data.json', 'r') as pd:
        personal_data = json.loads(pd.read())

    print('Personal Data Successfully Read!')


def fetch():
    read_personal_data()
    pw = pwd.check_pw(personal_data['hash'])
    cipher = pwd.AESCipher(pw)

    data_login = personal_data['login']
    data_login['userName'] = cipher.decrypt(data_login['userName'])
    data_login['password'] = cipher.decrypt(data_login['password'])

    print('Configurations Successfully Decrypted!')

    session = requests.Session()

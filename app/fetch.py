#!/usr/bin/env python3
import json
import requests

import defconst
import pwd


# Read Personal Data from JSON
def read_personal_data(json_file):
    with open(json_file, 'r') as pd:
        personal_data = json.loads(pd.read())

    print('Personal Data Successfully Read!')
    return personal_data


# Decrypt Login Data
def decrypt_login(data):
    pw = pwd.check_pw(data['hash'])
    cipher = pwd.AESCipher(pw)

    data_login = data['login']
    data_login['userName'] = cipher.decrypt(data_login['userName'])
    data_login['password'] = cipher.decrypt(data_login['password'])

    print('Configurations Successfully Decrypted!')
    return data_login


# Login from Main Page
def bb_login(data_login):
    login = session.post(
        url  = defconst.url['login'],
        data = data_login
    )

    print('Successfully Logged In!')
    return login


# LiveAgent Cookies
def la_cookie():
    csulb = session.get(url=defconst.url['csulb_html'])
    la_id = re.search(
        b'showWhenOnline\(\'(\w{15})\',',
        csulb.content
    )
    la_init = re.search(
        b'salesforceliveagent.com/chat\', \'(\w{15})\', \'(\w{15})\'',
        csulb.content
    )

    print('LiveAgent Configurations Got!')

    la = session.get(url=defconst.url['liveagent'].format(
        la_id.group(1).decode('utf-8'),
        la_init.group(1).decode('utf-8'),
        la_init.group(2).decode('utf-8')
    ))

    ssid = json.loads(la.content[27:-2])['messages'][0]['message']['sessionId']
    la_ck = defconst.la_cookies
    la_ck['liveagent_sid'] = la_ck['liveagent_ptid'] = ssid
    for x in la_ck.items():
        session.cookies.set(*x)

    print('LiveAgent Cookies Added!')


def fetch():
    personal_data = read_personal_data('data/data.json')
    data_login = decrypt_login(personal_data)

    session = requests.Session()
    print('Session Started!')

    login = bb_login(data_login)
    la_cookie()


def main(): # TODO: Other implementations
    fetch()


session = None

if __name__ == '__main__':
    main()

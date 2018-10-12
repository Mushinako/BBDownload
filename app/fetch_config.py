#!/usr/bin/env python3
import re
import json
import requests

import defconst
import pwd


# Read Personal Data from JSON
def read_personal_data(json_file):
    with open(json_file, 'r') as pd:
        defconst.data = json.loads(pd.read())

    print('Personal Data Successfully Read!')


# Decrypt Login Data
def decrypt_login():
    pwd.create_cipher()

    data_login = defconst.data['login']
    data_login['userName'] = defconst.cipher.decrypt(data_login['userName'])
    data_login['password'] = defconst.cipher.decrypt(data_login['password'])

    print('Configurations Successfully Decrypted!')


# Login from Main Page
def bb_login():
    print('Successfully Logged In!')
    return defconst.session.post(
        url  = defconst.url['login'],
        data = defconst.data['login']
    )


# Clear Login-Related Information
def clear_login():
    defconst.data['login'] = {}


# LiveAgent Cookies
def la_cookie():
    csulb = defconst.session.get(defconst.url['csulb_html'])
    la_id = re.search(
        b'showWhenOnline\(\'(\w{15})\',',
        csulb.content
    )
    la_init = re.search(
        b'salesforceliveagent.com/chat\', \'(\w{15})\', \'(\w{15})\'',
        csulb.content
    )

    print('LiveAgent Configurations Got!')

    la = defconst.session.get(url=defconst.url['liveagent'].format(
        la_id.group(1).decode('utf-8'),
        la_init.group(1).decode('utf-8'),
        la_init.group(2).decode('utf-8')
    ))

    ssid = json.loads(la.content[27:-2])['messages'][0]['message']['sessionId']
    la_ck = defconst.la_cookies
    la_ck['liveagent_sid'] = la_ck['liveagent_ptid'] = ssid
    for x in la_ck.items():
        defconst.session.cookies.set(*x)

    print('LiveAgent Cookies Added!')


# Fetch the Cookies and Configs
def fetch_config(read=True):
    if read:
        read_personal_data('data/data.json')

    defconst.session = requests.Session()
    print('Session Started!')

    decrypt_login()
    login = bb_login()
    clear_login()
    la_cookie()

    return login

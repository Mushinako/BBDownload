#!/usr/bin/env python3
import re
import json
import requests
import pwd
import defconst as d
import log as l


# Read Personal Data from JSON
def read_personal_data(json_file):
    with open(json_file, 'r') as pd:
        d.data = json.loads(pd.read())
    l.log('Personal Data Successfully Read!')


# Decrypt Login Data
def decrypt_login():
    pwd.create_cipher()
    d.lg = json.loads(json.dumps(d.data['login']))
    d.lg['userName'] = d.cipher.decrypt(d.lg['userName'])
    d.lg['password'] = d.cipher.decrypt(d.lg['password'])
    l.print_log('Configurations Successfully Decrypted!')


# Login from Main Page
def bb_login():
    l.print_log('Successfully Logged In!')
    return d.session.post(url = d.url['login'], data = d.lg)


# Clear Login-Related Information
def clear_login():
    d.lg = None


# LiveAgent Cookies
def la_cookie():
    csulb = d.session.get(d.url['csulb_html'])
    la_id = re.search(b'showWhenOnline\(\'(\w{15})\',',
                      csulb.content)
    la_init = re.search(
        b'salesforceliveagent.com/chat\', \'(\w{15})\', \'(\w{15})\'',
        csulb.content
        )
    l.log('LiveAgent Configurations Got!')
    la = d.session.get(url=d.url['liveagent'].format(
        la_id.group(1).decode('utf-8'),
        la_init.group(1).decode('utf-8'),
        la_init.group(2).decode('utf-8')
        ))
    ssid = json.loads(la.content[27:-2])['messages'][0]['message']['sessionId']
    la_ck = d.la_cookies
    la_ck['liveagent_sid'] = la_ck['liveagent_ptid'] = ssid
    for x in la_ck.items():
        d.session.cookies.set(*x)
    l.log('LiveAgent Cookies Added!')


# Fetch the Cookies and Configs
def fetch_config(read):
    if read:
        read_personal_data('data/data.json')
    d.session = requests.Session()
    l.log('Session Started!')
    decrypt_login()
    login = bb_login()
    clear_login()
    la_cookie()
    return login

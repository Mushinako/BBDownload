#!/usr/bin/env python3
import os
import re
import json
import getpass
import fetch_config
import pwd
import defconst


# Prompt User for Login Credentials
def prompt_login():
    defconst.login['userName'] = defconst.cipher.encrypt(
        input('Now Think of Your Student ID: ')
    ).decode('utf-8')
    defconst.login['password'] = defconst.cipher.encrypt(
        getpass.getpass('And Your CSULB Password: ')
    ).decode('utf-8')
    defconst.data['login'] = json.loads(json.dumps(defconst.login))
    print()


# Get OAuth Token
def get_oauth_token(login_content):
    token = defconst.session.post(
        defconst.url['oauth_token'],
        data = defconst.oauth_token,
        headers = {
            'x-csrf-token': re.search(
                b'\(\'XSRF.Token\',\'(\w{32})\'\);',
                login_content,
            ).group(1)
        }
    )
    print('OAuth Token Got!')
    return json.loads(token.content)['access_token']


# Authorization from JS
def js_auth(tk):
    auth_js = defconst.session.get(defconst.url['authjs'])
    auth = re.search(
        b'Authorization:\"(.*)\"\+n',
        auth_js.content
    ).group(1)
    print('Authorization Got!')
    return auth.decode('utf-8') + tk


# Get URL with List of Courses
def get_url_enroll(login_content):
    print('Enrollments URL Got!')
    return re.search(
        b'enrollments-url=\"([\w\-\.:/]*)\"',
        login_content
    ).group(1)


# Read List of Courses
def get_courses_list(url_enroll, auth):
    info_courses = defconst.session.get(
        url_enroll,
        headers = {'authorization': auth}
    )
    url_courses = json.loads(info_courses.content)['actions'][0]['href']
    list_courses = defconst.session.get(
        url_courses + defconst.course_para['list'],
        headers = {'authorization': auth}
    )
    infopage_courses = [
        (
            c['links'][1]['href'].split('/')[-1],
            c['links'][1]['href'] + defconst.course_para['info']
        )
        for c in json.loads(list_courses.content)['entities']
        if c['class'][1] == 'pinned'
    ]
    print('Courses List Got!')
    return infopage_courses


def get_dl(id_cour):
    dl_btn = defconst.session.get(defconst.url['dl_btn'].format(id_cour))
    try:
        dl_id = json.loads(
            json.loads(dl_btn.content[9:])['Data']['OR']['__g2']['1']
        )['P'][0]['P'][1]['P'][0]['Value']
    except:
        print('    No Contents!')
        return ''
    dl_init = defconst.session.get(
        defconst.url['dl_init'].format(id_cour, dl_id)
    )
    id_dl = re.search(
        b'\\\\/downloads\\\\/Course\\\\/(\d+)\\\\/',
        dl_init.content
    ).group(1)
    if id_dl is None:
        print('    No Contents!')
        return ''
    print('    Content URL Got!')
    return defconst.url['dl'].format(id_cour, id_dl.decode('utf-8'))


def get_ov(id_cour):
    url_ov = defconst.url['ov'].format(id_cour)
    ov = defconst.session.get(url_ov)
    if b'Internal Error' in ov.content:
        print('    No Overview!')
        return {
            'url' : '',
            'name': ''
        }
    ov_btn = defconst.session.get(defconst.url['ov_btn'].format(id_cour))
    ov_id = re.search(
        'data-title=\"([\w\_\.]+)\"',
        json.loads(ov_btn.content[9:])['Payload']['Html']
    ).group(1)
    print('    Overview URL Got!')
    return {
        'url' : url_ov,
        'name': ov_id
    }


# Get Info for Each Course
def get_info_courses(infopage_courses, auth):
    infodict_courses = {}
    print('\nGetting Course Data')
    for id_cour, url_cour in infopage_courses:
        info_cour = defconst.session.get(
            url_cour,
            headers = {'authorization': auth}
        )
        name_cour = re.search(
            '^(.+)\sSec',
            json.loads(info_cour.content)['properties']['name']
        ).group(1)
        print('  Getting {}...'.format(name_cour))
        dl = get_dl(id_cour)
        ov = get_ov(id_cour)
        # TODO: Get DL and INFO
        infodict_courses[name_cour] = {
            'name': name_cour,
            'no'  : id_cour,
            'dl'  : dl,
            'info': ov
        }
        print('  Course Info for {} Got!'.format(name_cour))
    return defconst.cipher.encrypt(json.dumps(infodict_courses))


# Write Personal Data to JSON
def write_json():
    if not os.path.isdir('data'):
        if os.path.isfile('data'):
            os.rename('data', 'data.bak')
        os.mkdir('data')
    if os.path.isfile('data/data.json'):
        if os.path.isfile('data/data.bak.json'):
            os.remove('data/data.bak.json')
        os.rename('data/data.json', 'data/data.bak.json')
    with open('data/data.json', 'w') as f:
        f.write(json.dumps(defconst.data, indent=4))


# Yeah Yeah Setup
def setup(refresh):
    if not refresh:
        defconst.data = {}
        defconst.data['hash'] = pwd.create_pw().decode('utf-8')
        prompt_login()
    try:
        if refresh:
            login = fetch_config.fetch_config(True)
        else:
            login = fetch_config.fetch_config(False)
            defconst.data['login'] = defconst.login
        print()
        auth = js_auth(get_oauth_token(login.content))
        infopage_courses = get_courses_list(
            get_url_enroll(login.content),
            auth
        )
        defconst.data['courses'] = get_info_courses(
            infopage_courses, auth
        ).decode('utf-8')
    except Exception as e:
        print(e)
        print('Error! Make Sure Your Credentials are Correct!')
    else:
        write_json()
        print()

#!/usr/bin/env python3
import os
import re
import json
import getpass
import fetch_config
import pwd
import defconst as d
import log as l


# Prompt User for Login Credentials
def prompt_login():
    d.login['userName'] = d.cipher.encrypt(
        input('Now Think of Your Student ID: ')
        ).decode('utf-8')
    d.login['password'] = d.cipher.encrypt(
        getpass.getpass('And Your CSULB Password: ')
        ).decode('utf-8')
    d.data['login'] = json.loads(json.dumps(d.login))
    print()


# Get OAuth Token
def get_oauth_token(login_content):
    token = d.session.post(
        d.url['oauth_token'],
        data = d.oauth_token,
        headers = {
            'x-csrf-token': re.search(
                b'\(\'XSRF.Token\',\'(\w{32})\'\);',
                login_content,
                ).group(1),
            }
        )
    l.log('OAuth Token Got!')
    return json.loads(token.content)['access_token']


# Authorization from JS
def js_auth(tk):
    auth_js = d.session.get(d.url['authjs'])
    auth = re.search(b'Authorization:\"(.*)\"\+n', auth_js.content).group(1)
    l.log('Authorization Got!')
    return auth.decode('utf-8') + tk


# Get URL with List of Courses
def get_url_enroll(login_content):
    l.print_log('Enrollments URL Got!')
    return re.search(
        b'enrollments-url=\"([\w\-\.:/]*)\"',
        login_content
        ).group(1)


# Read List of Courses
def get_courses_list(url_enroll, auth):
    info_courses = d.session.get(
        url_enroll,
        headers = {'authorization': auth,}
        )
    url_courses = json.loads(info_courses.content)['actions'][0]['href']
    list_courses = d.session.get(
        url_courses + d.course_para['list'],
        headers = {'authorization': auth,}
        )
    infopage_courses = [
        (
            c['links'][1]['href'].split('/')[-1],
            c['links'][1]['href'] + d.course_para['info']
            )
        for c in json.loads(list_courses.content)['entities']
        if c['class'][1] == 'pinned'
        ]
    l.print_log('Courses List Got!')
    return infopage_courses


def get_dl(id_cour):
    dl_btn = d.session.get(d.url['dl_btn'].format(id_cour))
    try:
        dl_candid = json.loads(dl_btn.content[9:])['Data']['OR']['__g2']
        dl_id = re.search(
            'openerId=(d2l_[0-9_]+)\\\\\"',
            json.dumps(dl_candid)
            ).group(1)
    except:
        l.print_log('    Content URL Parsing Error!')
        return ''
    dl_init = d.session.get(
        d.url['dl_init'].format(id_cour, dl_id)
        )
    id_dl = re.search(
        b'\\\\/downloads\\\\/Course\\\\/(\d+)\\\\/',
        dl_init.content
        ).group(1).decode('utf-8')
    if id_dl is None:
        l.print_log('    No Contents!')
        return ''
    l.print_log('    Content URL Got!')
    return [
        d.url['dl'].format(id_cour, id_dl),
        d.url['dl_check'].format(id_cour, id_dl, '{}'),
        ]


def get_ov(id_cour):
    url_ov = d.url['ov'].format(id_cour)
    ov = d.session.get(url_ov)
    if b'Internal Error' in ov.content:
        l.print_log('    No Overview!')
        return {'url' : '', 'name': ''}
    ov_btn = d.session.get(d.url['ov_btn'].format(id_cour))
    ov_id = re.search(
        'data-title=\"([\w\_\.]+)\"',
        json.loads(ov_btn.content[9:])['Payload']['Html']
        )
    if ov_id:
        l.print_log('    Overview URL Got!')
        return {
            'url' : url_ov,
            'name': ov_id.group(1),
            }
    l.print_log('    No Overview!')
    return {'url' : '', 'name': ''}


# Get Info for Each Course
def get_info_courses(infopage_courses, auth):
    infodict_courses = {}
    l.print_log('\nGetting Course Data')
    for id_cour, url_cour in infopage_courses:
        info_cour = d.session.get(
            url_cour,
            headers = {'authorization': auth,}
            )
        name_cour = re.search(
            '^(.+)\sSec',
            json.loads(info_cour.content)['properties']['name']
            ).group(1)
        l.print_log(f'  Getting {name_cour}...')
        dl, check = get_dl(id_cour)
        ov = get_ov(id_cour)
        # TODO: Get DL and INFO
        infodict_courses[name_cour] = {
            'name': name_cour,
            'no'  : id_cour,
            'dl'  : dl,
            'chk' : check,
            'info': ov,
        }
        l.print_log(f'  Course Info for {name_cour} Got!')
    return d.cipher.encrypt(json.dumps(infodict_courses))


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
        f.write(json.dumps(d.data, indent=4))


# Yeah Yeah Setup
def setup(refresh):
    if not refresh:
        d.data = {}
        d.data['hash'] = pwd.create_pw().decode('utf-8')
        prompt_login()
    try:
        if refresh:
            login = fetch_config.fetch_config(True)
        else:
            login = fetch_config.fetch_config(False)
            d.data['login'] = d.login
        print()
        auth = js_auth(get_oauth_token(login.content))
        infopage_courses = get_courses_list(
            get_url_enroll(login.content),
            auth
            )
        d.data['courses'] = get_info_courses(
            infopage_courses,
            auth
            ).decode('utf-8')
    except Exception as e:
        l.print_log(e)
        l.print_log('Error! Make Sure Your Credentials are Correct!')
    else:
        write_json()
        print()

#!/usr/bin/env python3
# Self-defined scripts
import v
from const import curls, plur
from file import Course
from err import login_chk, json_chk, re_chk, get_chk, post_chk


def get_urls():
    v.log_file.plog('-' * 24)
    v.log_file.plog('Getting login info...')
    # Login
    user_id, xsrf = login()
    # Authorization header
    auth(xsrf)
    # Get courses
    v.log_file.plog('Getting course info...')
    pin_courses = courses(user_id.decode('utf-8'))
    # Get files
    ovs = []
    files = []
    for cour in pin_courses:
        if cour.ov is not None:
            ovs.append(cour.ov)
        files += cour.files
    print('Got', plur(len(ovs), 'overview'), 'and',
          plur(len(files), 'other file'))
    return (ovs, files)


def login():
    v.log_file.pvlog('-' * 20)
    v.log_file.pvlog('Start login')
    login = post_chk(curls['login'], v.clogin_info, 'login')
    v.login_info = None
    login_sto = login_chk(login)
    v.log_file.plog('Successfully logged in!')
    return json_chk(['Session.UserId', 'XSRF.Token', ], login_sto, par=False,
                    mul=True)


def auth(xsrf):
    v.log_file.pvlog('-' * 20)
    v.log_file.pvlog('Start auth')
    # Token
    token_req = post_chk(curls['token'], {'scope': '*:*:*', }, 'token',
                         headers={'x-csrf-token': xsrf, })
    token = json_chk('access_token', token_req).encode('utf-8')
    v.log_file.pvlog('Got auth token')
    # Authorization header
    bsi = get_chk(curls['bsi'], 'bsi')
    auth_pre = re_chk(br'Authorization:`([\w ]+)\$\{token\}`', bsi,
                      'auth_pre')[1]
    v.log_file.pvlog('Got auth prefix')
    v.auth_head['Authorization'] = auth_pre + token
    v.log_file.pvlog('Auth set')


def courses(user_id):
    v.log_file.pvlog('-' * 20)
    v.log_file.pvlog('Start getting courses')
    all_courses_req = get_chk(
        curls['courses']+user_id, 'course list',
        headers=v.auth_head, params={'embedDepth': 1, }
        )
    all_courses = json_chk('entities', all_courses_req)
    pin_courses = []
    for cour in all_courses:
        cour_info = json_chk('class', cour, name='pinclass', par=False)
        cour_pin = json_chk(1, cour_info, name='pin', par=False)
        if cour_pin == 'pinned':
            cour_links = json_chk('links', cour, par=False)
            cour_li = json_chk(1, cour_links, par=False)
            cour_href = json_chk('href', cour_li, par=False)
            cr = Course(cour_href)
            print('  Got course:', cr.name)
            print('    Overview exists:', bool(cr.ov))
            print('    Number of other files:', len(cr.files))
            pin_courses.append(cr)
    v.log_file.plog('Courses got')
    return pin_courses

#!/usr/bin/env python3
import gc

# Self-defined scripts
import v
from const import curls, plur
from file import Course
from err import login_chk, json_par, json_chk, re_chk, get_chk, post_chk


def get_urls():
    '''Get the list of URLs of all files

    Returns:
        (List[str]): List of overview download links
        (List[str]): List of content download links
    '''
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
    '''Log into Beachboard

    Returns:
        (Dict[bytes]): Key-value pairs for tokens
    '''
    v.log_file.pvlog('-' * 20)
    v.log_file.pvlog('Start login')
    # Try logging in and get response
    login = post_chk(curls['login'], v.clogin_info, 'login')
    # Clear login info (though may not work)
    v.login_info = None
    gc.collect()
    # Check login response
    login_sto = login_chk(login)
    v.log_file.plog('Successfully logged in!')
    return (json_chk('Session.UserId', login_sto),
            json_chk('XSRF.Token', login_sto))


def auth(xsrf):
    '''Get cross-site authorization token

    Args:
        xsrf (bytes): XSRF token
    '''
    v.log_file.pvlog('-' * 20)
    v.log_file.pvlog('Start auth')
    # Token
    token_req = post_chk(curls['token'], {'scope': '*:*:*', }, 'token',
                         headers={'x-csrf-token': xsrf, })
    token_j = json_par(token_req, 'Auth token')
    token = json_chk('access_token', token_j).encode('utf-8')
    v.log_file.pvlog('Got auth token')
    # Authorization header
    bsi = get_chk(curls['bsi'], 'bsi')
    auth_pre = re_chk(br'Authorization:`([\w ]+)\$\{token\}`', bsi,
                      'auth_pre')[1]
    v.log_file.pvlog('Got auth prefix')
    # Set XS token to variable
    v.auth_head['Authorization'] = auth_pre + token
    v.log_file.pvlog('Auth set')


def courses(user_id):
    '''Get list of courses with info

    Args:
        user_id (str): User ID
    Returns:
        (List[Course]): List of courses (pinned)
    '''
    v.log_file.pvlog('-' * 20)
    v.log_file.pvlog('Start getting courses')
    # Get list of courses
    all_courses_req = get_chk(
        curls['courses']+user_id, 'course list',
        headers=v.auth_head, params={'embedDepth': 1, }
        )
    courses_j = json_par(all_courses_req, 'All courses')
    all_courses = json_chk('entities', courses_j)
    pin_courses = []
    for cour in all_courses:
        # Check if course is pinned
        cour_info = json_chk('class', cour, name='pinclass')
        cour_pin = json_chk(1, cour_info, name='pin')
        if cour_pin == 'pinned':
            # Get course main link
            cour_links = json_chk('links', cour)
            cour_li = json_chk(1, cour_links)
            cour_href = json_chk('href', cour_li)
            # Construct course object
            cr = Course(cour_href)
            print('  Got course:', cr.name)
            print('    Overview exists:', bool(cr.ov))
            print('    Number of other files:', len(cr.files))
            pin_courses.append(cr)
    v.log_file.plog('Courses got')
    return pin_courses

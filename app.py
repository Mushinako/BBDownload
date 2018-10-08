#!/usr/bin/env python3
import re
import os
import bcrypt
import sys
import json
from shutil import rmtree
from getpass import getpass
from zipfile import ZipFile, BadZipfile
from pathlib import Path
from requests import Session
from base64 import b64encode, b64decode
from hashlib import sha256, md5, sha1
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:
    def __init__(self, key):
        self.key = sha256(key).digest()

    def encrypt(self, data):
        iv = Random.new().read(AES.block_size)
        c = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + c.encrypt(self._pad(data).encode('utf-8')))

    def decrypt(self, data):
        data = b64decode(data)
        c = AES.new(self.key, AES.MODE_CBC, data[:AES.block_size])
        return self._unpad(c.decrypt(data[AES.block_size:])).decode('utf-8')

    def _pad(self, data):
        k = AES.block_size - len(data) % AES.block_size
        return data + k * chr(k)

    @staticmethod
    def _unpad(data):
        return data[:-data[-1]]


class FileData:
    def __init__(self, path):
        self.path = path
        self.size = os.stat(path).st_size
        self.md5 = None
        self.sha1 = None
        self.hashes = None

    def hash(self):
        m = md5()
        s = sha1()
        with open(self.path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                m.update(data)
                s.update(data)
        self.md5 = m.hexdigest()
        self.sha1 = s.hexdigest()
        self.hashes = [self.md5, self.sha1]


def check_pw(pw_hash):
    pw = getpass().encode('utf-8')
    hashed = pw_hash.encode('utf-8')
    print()

    if hashed == bcrypt.hashpw(pw, hashed):
        return pw
    else:
        print('Password no match!')
        print('Make sure you use the password set up in this app!')
        sys.exit()


def setup_and_fetch(setup):
    with open('data.json', 'r') as json_data:
        data = json.loads(json_data.read())
    print('Configurations Successfully Read!')

    pw = check_pw(data['hash'])

    data_login = data['data']['login']
    cipher = AESCipher(pw)
    data_login['userName'] = cipher.decrypt(data_login['userName'])
    data_login['password'] = cipher.decrypt(data_login['password'])

    urls = data['urls']
    session = Session()
    print('Session Started!')

    # Login from Main Page
    login = session.post(
        url = urls['login'],
        data = data_login
        )
    print('Successfully Logged In!')

    if True:   # TODO: setup
        COURSES_LIST_PARA = ('?search=&pageSize=20&embedDepth=1'
                             '&sort=-PinDate,OrgUnitName,OrgUnitId'
                             '&parentOrganizations=&orgUnitTypeId=3'
                             '&promotePins=false&autoPinCourses=true&roles='
                             '&excludeEnded=false')
        COURSES_INFO_PARA = '?embedDepth=1'

        # Get Oauth Token
        token = session.post(
            url = urls['token'],
            data = data['data']['token'],
            headers = {
                'x-csrf-token': re.search(
                    b'\(\'XSRF.Token\',\'(\w{32})\'\);',
                    login.content
                    ).group(1)
                }
            )
        tk = json.loads(token.content)['access_token']
        print('OAuth Token Got!')

        # Get Authorization
        auth_js = session.get(url=urls['authjs'])
        auth = re.search(
            b'Authorization:\"(.*)\"\+n',
            auth_js.content
            ).group(1)

        auth = auth.decode('utf-8') + tk
        print('Authorization Got!')

        # Get Enrollments URL
        enroll_url = re.search(
            b'enrollments-url=\"([\w\-\.:/]*)\"',
            login.content
            ).group(1)
        print('Enrollments URL Got!')

        # Get Courses List
        courses_info = session.get(
            url = enroll_url,
            headers = {'authorization': auth}
            )
        courses_url = json.loads(courses_info.content)['actions'][0]['href']
        courses_list = session.get(
            url = courses_url + COURSES_LIST_PARA,
            headers = {'authorization': auth}
            )
        courses_infopage = [
            [
                c['links'][1]['href'].split('/')[-1],
                c['links'][1]['href'] + COURSES_INFO_PARA
                ]
            for c in json.loads(courses_list.content)['entities']
            if c['class'][1] == 'pinned'
            ]
        print('Courses List Got!')

        # Get Info for Each Course
        courses_infodict = {}
        for cour_id, cour_url in courses_infopage:
            cour_info = session.get(
                url = cour_url,
                headers = {'authorization': auth}
            )
            cour_name = json.loads(cour_info.content)['properties']['name']
            courses_infodict[cour_id] = {
                'name': cour_name,
                'no': cour_id
            }
            print('Courses Info for {} Got!'.format(cour_name))

            course_content = session.get(url=urls['content'].format(cour_id))
            print('\n{}\n'.format(course_content.content))

        # print('\n\n{}\n\n'.format(courses_infodict))

    # CSULB Page
    csulb = session.get(url=urls['csulb'])
    la_init = re.search(
        b'salesforceliveagent.com/chat\', \'(\w{15})\', \'(\w{15})\'',
        csulb.content
        )
    la_id = re.search(
        b'showWhenOnline\(\'(\w{15})\',',
        csulb.content
        )
    print('LiveAgent Configurations Got!')

    # LiveAgent Cookies
    la = session.get(
        url = urls['liveagent'].format(
            la_id.group(1).decode('utf-8'),
            la_init.group(1).decode('utf-8'),
            la_init.group(2).decode('utf-8')
            )
        )
    la_ck = data['cookies']['liveagent']
    ssid = json.loads(la.content[27:-2])['messages'][0]['message']['sessionId']
    la_ck['liveagent_ptid'] = la_ck['liveagent_sid'] = ssid
    for x in la_ck.items():
        session.cookies.set(*x)
    print('LiveAgent Cookies Added!')

    # # Iterate Thru Courses
    # courses = json.loads(cipher.decrypt(data['courses']))
    # for course, prop in courses.items():
    #     print()
    #     name = prop['name']
    #     print('Downloading Content for {}...'.format(name))
    #     # Create Folders as Necessary
    #     temp_course = 'Temp\\{}'.format(name)
    #     Path(temp_course).mkdir(parents=True)
    #
    #     #Content Download
    #     dl_url = prop['dl']
    #     if dl_url == '':
    #         print('  No Contents!')
    #     else:
    #         print('  Downloading Contents...')
    #         dl = session.get(url=dl_url)
    #         zip_name = '{0}\\{1}.zip'.format(temp_course, name)
    #         with open(zip_name, 'wb') as f:
    #             f.write(dl.content)
    #         print('  Contents Downloaded!')
    #         print('  Extracting Contents...')
    #         try:
    #             with ZipFile(zip_name, 'r') as z:
    #                 z.extractall(temp_course)
    #         except BadZipfile:
    #             print('    Content for {} is not a Zip File!'.format(name))
    #         print('  Contents Extracted!')
    #         os.remove(zip_name)
    #
    #     # Overview Download
    #     ov_url = prop['info']
    #     if ov_url == '':
    #         print('  No Overview!')
    #     else:
    #         print('  Downloading Overview...')
    #         ov = session.get(url=ov_url)
    #         with open('{}\\Overview.pdf'.format(temp_course), 'wb') as f:
    #             f.write(ov.content)
    #         print('  Overview Downloaded!')
    #
    #     # Merge to Main Folder
    #     print()
    #     print('Merging {} to Main Folder...'.format(name))
    #     main_course = 'Contents\\{}'.format(name)
    #
    #     # os.walk Returns [folder_name, sub_folders, sub_files]
    #     for temp_folder, _, files in os.walk(temp_course):
    #         rel_path = '\\'.join(temp_folder.split('\\')[1:])
    #         print('  Merging Folder {}...'.format(rel_path))
    #         print('  Files Present: {}'.format(files))
    #         main_folder = '{0}\\{1}'.format(
    #             main_course,
    #             '\\'.join(temp_folder.split('\\')[2:])
    #         )
    #         Path(main_folder).mkdir(parents=True, exist_ok=True)
    #
    #         # Copy to Main Folder
    #         for file in files:
    #             print('    Merging File {0}\\{1}...'.format(rel_path, file))
    #             temp_file = '{0}\\{1}'.format(temp_folder, file)
    #             main_file = re.sub(' \(\d+\).', '.', '{0}\\{1}'.format(main_folder, file))
    #             while main_file[0] == ' ':
    #                 main_file = main_file[1:]
    #
    #             # Check If File With Same Name Exists
    #             if os.path.isfile(main_file):
    #                 print('      File Name Collision!')
    #                 f_temp = FileData(temp_file)
    #                 f_main = FileData(main_file)
    #
    #                 # If File with Same Name Exists, Check Size
    #                 if f_temp.size == f_main.size:
    #                     print('      File Size Collision!')
    #                     f_temp.hash()
    #                     f_main.hash()
    #
    #                     # If File with Same Size Exists, Check Hash
    #                     assert None not in f_temp.hashes + f_main.hashes, 'Hash Calculations Failed!'
    #                     if f_temp.md5 == f_main.md5 and f_temp.sha1 == f_main.sha1:
    #                         print('      File Hash Collision!')
    #                         os.remove(temp_file)
    #                         print('      File Merged!')
    #                         continue
    #
    #                 # If Same File Name with Different Sizes/Hashes, Rename New File with Appendixes
    #                 old_file = main_file.split('.')
    #                 num = 1
    #
    #                 # Try unused numbers
    #                 while True:
    #                     f = '{0} {1}.{2}'.format(
    #                         '.'.join(old_file[:-1]),
    #                         num,
    #                         old_file[-1]
    #                         )
    #                     if os.path.exists(f):
    #                         num += 1
    #                     else:
    #                         os.rename(temp_file, f)
    #                         print('      File Renamed as {}!'.format(f))
    #
    #             # Directly Move the File If No File with the Same Name Exists
    #             else:
    #                 os.rename(temp_file, main_file)
    #                 print('      File Copied!')
    #
    # print()
    #
    # # Get Rid of Empty Folders, Lazy Method
    # for _ in range(2):
    #     for dirpath, directories, files in os.walk('Contents', topdown=False):
    #         if not directories and not files:
    #             os.rmdir(dirpath)
    # print('Empty Folders Cleared!')


def main():
    HELP = '''
    This project is distributed under GPLv3 by Mushinako. This project comes
    with absolutely NO warranty, and I am NOT responsible for any data loss
    and/or leak. Please only test this script if you understand what you and
    this script are doing!

    This short script grabs all files from BeachBoard @ CSULB (hopefully),
    unless the system breaks (which occurs often) or have some major changes.

    [This program needs to be setup at the first time, asking you for your
    credentials, and a file named "data.json" should appear, storing
    necessary data. This file will refresh once every 5 times the program is
    run. (FUTURE)]

    You also need a password, ideally different from your CSULB password, to
    encrypt the latter in the file. You will need this password EVERY time you
    run this program, as you need to decrypt your CSULB password every time.

    The same file will not be overwritten, but different files with the same
    name (possibly different versions) will be renamed by attaching " (1)",
    " (2)", etc.

    ARGUMENTS:
    -h, --help      Show this text
    -r, --reset     Force reset. "data.json" will be deleted and you will
                    need to re-setup. You may likely have to do this every
                    semester.
    '''

    if len(sys.argv) == 1:
        if os.path.isfile('data.json'):
            try:
                setup_and_fetch(False)
            except BadZipfile:
                pass
            finally:
                if os.path.isdir('Temp'):
                    rmtree('Temp')
                print()
        # (FUTURE)
        # else:
            # setup_and_fetch(True)
    elif sys.argv[1] in ['-h', '--help']:
        print(HELP)
    # (FUTURE)
    # elif sys.argv[1] not in ['-r', '--reset']:
    #     setup_and_fetch(True)
    else:
        raise ValueError('''
            Invalid arguments!
            Use '-h' or '--help' to access help!
            ''')


if __name__ == '__main__':
    main()

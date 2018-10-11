#!/usr/bin/env python3
import os
import json
import pathlib
import zipfile

import pwd
import defconst


# Decrypt Courses Data
def decrypt_courses():
    return json.loads(pwd.create_cipher().decrypt(defconst.data['courses']))


# Create Folders as Necessary
def create_dir(name):
    temp_course = 'Temp/{}'.format(name)
    pathlib.Path(temp_course).mkdir(parents=True)
    return temp_course


# Content Download
def dl_content(temp_course, name):
    dl_url = prop['dl']
    if dl_url == '':
        print('  No Contents!')
    else:
        print('  Downloading Contents...')

        dl = defconst.session.get(url=dl_url)
        zip_name = '{0}/{1}.zip'.format(temp_course, name)

        with open(zip_name, 'wb') as f:
            f.write(dl.content)

        print('  Contents Downloaded!')
        print('  Extracting Contents...')

        try:
            with zipfile.ZipFile(zip_name, 'r') as z:
                z.extractall(temp_course)
        except zipfile.BadZipFile:
            print('    Content for {} is not a ZipFile!'.format(name))
        else:
            print('  Contents Extracted!')
        finally:
            os.remove(zip_name)


# Overview Download
def dl_overview(temp_course):
    ov_url = prop['info']
    if ov_url == '':
        print('  No Overview!')
    else:
        print('  Downloading Overview...')

        ov = session.get(url=ov_url)

        with open('{}/Overview.pdf'.format(temp_course), 'wb') as f:
            f.write(ov.content)

        print('  Overview Downloaded!')


def merge_file(rel_path, file):
    print('    Merging File {0}/{1}...'.format())


# Merge Temp to Contents
def merge_to_main(temp_course, name):
    print('Merging {} to Main Folder...'.format(name))

    main_course = 'Contents/{}'.format(name)

    # os.walk Returns [folder_name, sub_folders, sub_files]
    for temp_folder, _, files in os.walk(temp_course):
        temp_folder = temp_folder.replace('\\', '/')

        rel_path = '/'.join(temp_folder.split('/')[1:])

        print('  Merging Folder {}...'.format(rel_path))
        print('  Files Present: {}'.format(files))

        main_folder = '{0}/{1}'.format(
            main_course,
            '/'.join(temp_folder.split('/')[2:])
        )

        pathlib.Path(main_folder).mkdir(parents=True, exist_ok=True)

        for file in files:
            merge_file(rel_path, file)


# Fetch Files
def fetch_files():
    courses = decrypt_courses()

    # Iterate Through Courses
    for course, prop in courses.items():
        print()

        name = prop['name']
        print('Downloading Content for {}...'.format(name))

        temp_course = create_dir(name)

        dl_content(temp_course, name)
        dl_overview(temp_course)

        print()

        merge_to_main(temp_course, name)
    pass

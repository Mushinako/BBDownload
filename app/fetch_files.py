#!/usr/bin/env python3
import os
import re
import json
import pathlib
import zipfile

import pwd
import defconst
import filedata


# Decrypt Courses Data
def decrypt_courses():
    return json.loads(defconst.cipher.decrypt(defconst.data['courses']))


# Create Folders as Necessary
def create_dir(name):
    temp_course = 'Temp/{}'.format(name)
    pathlib.Path(temp_course).mkdir(parents=True, exist_ok=True)
    return temp_course


# Content Download
def dl_content(temp_course, name, dl_url):
    if dl_url == '':
        print('  No Contents!')
        return

    print('  Downloading Contents...')

    dl = defconst.session.get(dl_url)
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
        print('      Try Refreshing URLs with -c')
    else:
        print('  Contents Extracted!')
    finally:
        os.remove(zip_name)


# Overview Download
def dl_overview(temp_course, ov_url):
    if ov_url['url'] == '':
        print('  No Overview!')
        return

    print('  Downloading Overview...')

    ov = defconst.session.get(url=ov_url['url'])

    with open('{}/{}'.format(temp_course, ov_url['name']), 'wb') as f:
        f.write(ov.content)

    print('  Overview Downloaded!')


# Check File Collision
def check_collision(f_temp, f_main, temp_file):
    # If File with Same Name Exists, Check Size
    if f_temp.size == f_main.size:
        print('      File Size Collision!')
        f_temp.hash()
        f_main.hash()

        assert None not in (f_temp.hashes + f_main.hashes), ('Hash '
            'Calculations Failed!')

        # If File with Same Size Exists, Check Hash
        if f_temp.hashes == f_main.hashes:
            print('      File Hash Collision!')
            os.remove(temp_file)
            print('      File Merged!')
            return True

    return False


# Copy File and Merge
def merge_file(rel_path, file, temp_folder, main_folder):
    print('    Merging File {0}/{1}...'.format(rel_path, file))
    temp_file = '{0}/{1}'.format(temp_folder, file)
    main_file = re.sub(
        '\s+\(\d+\).',
        '.',
        '{0}/{1}'.format(main_folder, file)
    ).strip()

    # Check if File with Same Name Exists
    if os.path.isfile(main_file):
        print('      File Name Collision!')
        f_temp = filedata.FileData(temp_file)
        f_main = filedata.FileData(main_file)

        if check_collision(f_temp, f_main, temp_file):
            return

        # If Same File Name with Different Sizes/Hashes
        # Rename New Files with Appendices
        old_file = main_file.split('.')
        num = 1

        # Try Finding First Unused Number
        while True:
            f = '{0} ({1}).{2}'.format(
                '.'.join(old_file[:-1]),
                num,
                old_file[-1]
            )
            if os.path.exists(f):
                if check_collision(f_temp, filedata.FileData(f), temp_file):
                    return
                num += 1
            else:
                os.rename(temp_file, f)
                print('      File Renamed as {}!'.format(f))

        return

    # Directly Move the File If No File with the Sams Name Exists
    os.rename(temp_file, main_file)
    print('      File Copied!')


# Merge Temp to Contents
def merge_to_main(temp_course, name):
    print('Merging {} to Main Folder...'.format(name))

    main_course = 'Contents/{}'.format(name)

    # os.walk Returns [folder_name, sub_folders, sub_files]
    for temp_folder, _, files in os.walk(temp_course):
        temp_folder = temp_folder.replace('\\', '/')

        rel_path = '/'.join(temp_folder.split('/')[1:])

        print('  Merging Folder {}...'.format(rel_path))
        # print('  Files Present: {}'.format(files))    # Disabled. Too Long

        main_folder = '{0}/{1}'.format(
            main_course,
            '/'.join(temp_folder.split('/')[2:])
        )

        pathlib.Path(main_folder).mkdir(parents=True, exist_ok=True)

        for file in files:
            merge_file(rel_path, file, temp_folder, main_folder)


# Get Rid of Empty Folders, Lazy Method
def rmdir_empty():
    for _ in range(2):
        for dir_path, dirs, files in os.walk('Contents', topdown=False):
            if not dirs and not files:
                os.rmdir(dir_path)

    print('Empty Folders Cleared!')


# Fetch Files
def fetch_files():
    courses = decrypt_courses()

    # Iterate Through Courses
    for course, prop in courses.items():
        print()

        name = prop['name']
        print('Downloading Content for {}...'.format(name))

        temp_course = create_dir(name)

        dl_content(temp_course, name, prop['dl'])
        dl_overview(temp_course, prop['info'])

        print()

        merge_to_main(temp_course, name)

    print()

    rmdir_empty()

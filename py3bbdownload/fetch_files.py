#!/usr/bin/env python3
import os
import sys
import re
import json
import pathlib
import zipfile
import ctypes
import pwd
import defconst
import filedata


# Decrypt Courses Data
def decrypt_courses():
    return json.loads(defconst.cipher.decrypt(defconst.data['courses']))


# Create Folders as Necessary
def create_dir(name):
    temp_course = os.path.join('.temp', name)
    pathlib.Path(temp_course).mkdir()
    return temp_course


# Content Download
def dl_content(temp_course, name, dl_url):
    if dl_url == '':
        print('  No Contents!')
        return
    print('  Downloading Contents...')
    dl = defconst.session.get(dl_url)
    zip_name = os.path.join(temp_course, name+'.zip')
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
    with open(os.path.join(temp_course, ov_url['name']), 'wb') as f:
        f.write(ov.content)
    print('  Overview Downloaded!')


# Check File Collision
def check_collision(f_temp, f_main, temp_file):
    # If File with Same Name Exists, Check Size
    if f_temp.size == f_main.size:
        print('      File Size Collision!')
        f_temp.hash()
        f_main.hash()
        if None in (f_temp.hashes + f_main.hashes):
            print('Hash Calculations Failed!')
            sys.exit()
        # If File with Same Size Exists, Check Hash
        if f_temp.hashes == f_main.hashes:
            print('      File Hash Collision!')
            os.remove(temp_file)
            print('      File Merged!')
            return True
    return False


# Copy File and Merge
def merge_file(rel_path, file, temp_folder, main_folder):
    print('    Merging File {}...'.format(os.path.join(rel_path, file)))
    temp_file = os.path.join(temp_folder, file)
    main_file = re.sub('\s+\(\d+\).', '.', os.path.join(main_folder, file)
                       ).strip().replace('//', '/')
    # Always Overwrite the Contents
    if file == 'Table of Contents.html':
        if os.path.isfile(main_file):
            os.remove(main_file)
    # Check if File with Same Name Exists
    elif os.path.isfile(main_file):
        print('      File Name Collision!')
        f_temp = filedata.FileData(temp_file)
        f_main = filedata.FileData(main_file)
        if check_collision(f_temp, f_main, temp_file):
            return False
        # If Same File Name with Different Sizes/Hashes
        # Rename New Files with Appendices
        old_file = main_file.split('.')
        num = 1
        # Try Finding First Unused Number
        while True:
            f = '{0} ({1}).{2}'.format('.'.join(old_file[:-1]), num,
                                       old_file[-1])
            if os.path.exists(f):
                if check_collision(f_temp, filedata.FileData(f), temp_file):
                    return False
                num += 1
            else:
                os.rename(temp_file, f)
                print('      File Renamed as {}!'.format(f))
                return [1, main_file]
    # Directly Move the File If No File with the Same Name Exists
    os.rename(temp_file, main_file)
    print('      File Copied!')
    if file == 'Table of Contents.html':
        return False
    return [0, main_file]


# Merge Temp to Contents
def merge_to_main(temp_course, name):
    print('Merging {} to Main Folder...'.format(name))
    main_course = os.path.join('Contents', name)
    changes = [[], []]  # [new, modified]
    # os.walk Returns [folder_name, sub_folders, sub_files]
    for temp_folder, _, files in os.walk(temp_course):
        temp_folder = temp_folder.replace('\\', '/')
        rel_path = '/'.join(temp_folder.split('/')[1:])
        print('  Merging Folder {}...'.format(rel_path))
        # print('  Files Present: {}'.format(files))    # Disabled. Too Long
        main_folder = os.path.join(main_course,
                                   '/'.join(temp_folder.split('/')[2:]))
        pathlib.Path(main_folder).mkdir(parents=True, exist_ok=True)
        for file in files:
            change = merge_file(rel_path, file, temp_folder, main_folder)
            if change:
                changes[change[0]].append(change[1])
    return changes


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
    changes = {}
    # Make and Hide Temp Folder
    pathlib.Path('.temp').mkdir()
    if os.name == 'nt':
        if not ctypes.windll.kernel32.SetFileAttributesW('.temp', 0x02):
            print('Temp Folder not Hidden')
    # Iterate Through Courses
    for course, prop in courses.items():
        print()
        name = prop['name']
        print('Downloading Content for {}...'.format(name))
        temp_course = create_dir(name)
        dl_content(temp_course, name, prop['dl'])
        dl_overview(temp_course, prop['info'])
        print()
        changes[course] = merge_to_main(temp_course, name)
    print()
    rmdir_empty()
    print()
    print('Changes:')
    for course, changes in changes.items():
        print(' ', course)
        print('    New:')
        for x in changes[0]:
            print('     ', x)
        print('    Modified:')
        for x in changes[1]:
            print('     ', x)

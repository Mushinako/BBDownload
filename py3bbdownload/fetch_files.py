#!/usr/bin/env python3
import os
import sys
import re
import math
import json
import time
import pathlib
import shutil
import zipfile
import ctypes
import filedata
import importlib
import pwd
import defconst as d
import log as l

HAS_TQDM = (importlib.util.find_spec('tqdm') and (
    os.name!='nt' or importlib.util.find_spec('colorama')
    )) is not None
if HAS_TQDM:
    import tqdm
    import colorama


# Decrypt Courses Data
def decrypt_courses():
    return json.loads(d.cipher.decrypt(d.data['courses']))


# Create Folders as Necessary
def create_dir(name):
    temp_course = os.path.join('.temp', name)
    pathlib.Path(temp_course).mkdir()
    return temp_course


# Content Download
def dl_content(temp_course, name, dl_url, dl_check):
    if dl_url == '':
        l.print_log('  No Contents!')
        return
    l.print_log('  Downloading Contents...')
    i = 2
    while True:
        status = d.session.get(dl_check.format(i))
        try:
            stat_text = json.loads(status.content[9:])['Payload']['JobStatus']
        except KeyError:
            l.print_log('    Unprecedented status format!')
            break
        else:
            if stat_text == 'Successful':
                l.print_log('    File is ready for download')
                break
            elif stat_text == 'Processing':
                i += 1
                l.print_log('    Server is packaging files...')
                time.sleep(5)
            else:
                l.print_log('    Unprecedented status message!')
    dl = d.session.get(dl_url, stream=True)
    dl_len = dl.headers.get('content-length')
    zip_name = os.path.join(temp_course, name+'.zip')
    MARK_STEP = 5
    with open(zip_name, 'wb') as f:
        if dl_len is None:
            l.print_log('    Downloading...')
            f.write(dl.content)
        elif HAS_TQDM:
            l.log('    Downloading, progress with tqdm...')
            for data in tqdm.tqdm(
                dl.iter_content(1024),
                desc=name,
                total=math.ceil(int(dl_len)/10.24)/100,
                ascii=True,
                unit='KiB'
                ):
                f.write(data)
        else:
            dl_len = int(dl_len)
            dl_ed = 0
            dl_mark = MARK_STEP
            for data in dl.iter_content(4096):
                dl_ed += len(data)
                f.write(data)
                if dl_ed/dl_len*100 >= dl_mark:
                    l.print_log(f'    Downloaded {dl_mark}%')
                    dl_mark += MARK_STEP
    l.print_log('  Contents Downloaded!')
    l.print_log('  Extracting Contents...')
    try:
        with zipfile.ZipFile(zip_name, 'r') as z:
            z.extractall(temp_course)
    except zipfile.BadZipFile:
        l.print_log(f'    Content for {name} is not a ZipFile!')
        debug_zip_name = os.path.join('Debug', name)
        shutil.copyfile(zip_name, debug_zip_name)
        l.print_log(f'    Copied tp {debug_zip_name}!')
    else:
        l.print_log('  Contents Extracted!')
    finally:
        os.remove(zip_name)


# Overview Download
def dl_overview(temp_course, ov_url):
    if ov_url['url'] == '':
        l.print_log('  No Overview!')
        return
    l.print_log('  Downloading Overview...')
    ov = d.session.get(url=ov_url['url'])
    with open(os.path.join(temp_course, ov_url['name']), 'wb') as f:
        f.write(ov.content)
    l.print_log('  Overview Downloaded!')


# Check File Collision
def check_collision(f_temp, f_main, temp_file):
    # If File with Same Name Exists, Check Size
    if f_temp.size == f_main.size:
        l.log('      File Size Collision!')
        f_temp.hash()
        f_main.hash()
        if None in (f_temp.hashes + f_main.hashes):
            l.print_log('Hash Calculations Failed!')
            sys.exit()
        # If File with Same Size Exists, Check Hash
        if f_temp.hashes == f_main.hashes:
            l.log('      File Hash Collision!')
            os.remove(temp_file)
            l.print_log('      File Merged!')
            return True
    return False


# Copy File and Merge
def merge_file(rel_path, file, temp_folder, main_folder):
    l.print_log(f'    Merging File {os.path.join(rel_path, file)}...')
    temp_file = os.path.join(temp_folder, file)
    main_file = re.sub('\s+\(\d+\).', '.', os.path.join(main_folder, file)
                       ).strip().replace('//', '/')
    # Always Overwrite the Contents
    if file == 'Table of Contents.html':
        if os.path.isfile(main_file):
            os.remove(main_file)
    # Check if File with Same Name Exists
    elif os.path.isfile(main_file):
        l.log('      File Name Collision!')
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
            f = f"{'.'.join(old_file[:-1])} ({num}).{old_file[-1]}"
            if os.path.exists(f):
                if check_collision(f_temp, filedata.FileData(f), temp_file):
                    return False
                num += 1
            else:
                os.rename(temp_file, f)
                l.print_log(f'      File Renamed as {f}!')
                return [1, main_file]
    # Directly Move the File If No File with the Same Name Exists
    os.rename(temp_file, main_file)
    l.print_log('      File Copied!')
    if file == 'Table of Contents.html':
        return False
    return [0, main_file]


# Merge Temp to Contents
def merge_to_main(temp_course, name):
    l.print_log(f'Merging {name} to Main Folder...')
    main_course = os.path.join('Contents', name)
    changes = [[], []]  # [new, modified]
    # os.walk Returns [folder_name, sub_folders, sub_files]
    for temp_folder, _, files in os.walk(temp_course):
        temp_folder = temp_folder.replace('\\', '/')
        rel_path = os.path.join(*temp_folder.split('/')[1:])
        l.print_log(f'  Merging Folder {rel_path}...')
        l.print_log(f'  Files Present: {files}')
        main_folder = os.path.join(
            main_course,
            *temp_folder.split('/')[2:])
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
    l.print_log('Empty Folders Cleared!')


# Fetch Files
def fetch_files():
    courses = decrypt_courses()
    changes = {}
    # Make and Hide Temp Folder
    pathlib.Path('.temp').mkdir()
    if os.name == 'nt':
        if not ctypes.windll.kernel32.SetFileAttributesW('.temp', 0x02):
            l.print_log('Temp Folder not Hidden')
    # Iterate Through Courses
    for course, prop in courses.items():
        print()
        name = prop['name']
        l.print_log(f'Downloading Content for {name}...')
        temp_course = create_dir(name)
        dl_content(temp_course, name, prop['dl'], prop['chk'])
        dl_overview(temp_course, prop['info'])
        print()
        changes[course] = merge_to_main(temp_course, name)
    print()
    rmdir_empty()
    print()
    l.print_log('Changes:')
    for course, changes in changes.items():
        l.print_log(' ', course)
        l.print_log('    New:')
        for x in changes[0]:
            l.print_log('     ', x)
        l.print_log('    Modified:')
        for x in changes[1]:
            l.print_log('     ', x)

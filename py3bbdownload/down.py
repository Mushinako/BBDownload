#!/usr/bin/env python3
import os
from math import ceil
from re import search
from shutil import get_terminal_size
from urllib.parse import unquote
from pathlib import Path

# Self-defined scripts
import v
from const import cs, cfiles, cdirs, plur
from move import move_file
from log import vprint


def down(ovs, files):
    v.log_file.plog('-' * 24)
    v.log_file.plog('Downloading files...')
    fai = []    # List of failed downloads
    new = []    # List of new files
    upd = []    # List of updated files
    tot = 0     # Total file size
    # Download overviews
    tl = len(ovs) + len(files)
    fi = 0
    for ov in ovs:
        fi += 1
        fai, new, upd, tot = df(ov, dov, fai, new, upd, tot, fi, tl)
    # Download files
    for file in files:
        fi += 1
        fai, new, upd, tot = df(file, dfile, fai, new, upd, tot, fi, tl)
    # Total size
    gib = ' ({:.3f} GiB)'.format(tot/1024) if tot >= 1000 else ''
    print('-' * 30)
    print('Size of all files downloaded: {:.3f} MiB'.format(tot) + gib)
    # Write list of fails
    writes('Download failures', cfiles['fail_file'], fai)
    # Write list of new files
    writes('New files', cfiles['new_file'], new)
    # Write list of updates
    writes('Updated files', cfiles['upd_file'], upd)


def writes(prompt, fn, arr):
    fi = plur(len(arr), 'file')
    print(prompt, '(Detail in {0}):'.format(fn), fi)
    if arr:
        with open(fn, 'w') as f:
            print(fi+':', file=f)
            for e in arr:
                vprint(' ', e.format(''))
                print(' ', e.format(''), file=f)
    else:
        vprint('  None')


def df(file, func, fails, new, upd, tot, fi, tl):
    v.log_file.plog(' ', '-' * 18)
    tl = str(tl)
    fid = str(fi).rjust(len(tl)) + '/' + tl
    success, ext, leng = func(file, fid)
    file_tmp = file.name+'{}'+ext
    path_tmp = os.path.join(file.folder, file_tmp)
    if success:
        suc_msg = ('  ' + file_tmp.format('')
                   + ' successfully downloaded! ({:.3f} MiB)'.format(leng))
        spaces = ' ' * max(get_terminal_size().columns - len(suc_msg), 0)
        print(suc_msg + spaces)
        stat = move_file(file.folder, path_tmp, file_tmp.format(r'-\d{14}'))
        print('  File moved!')
        if stat == 1:
            upd.append(path_tmp)
        elif stat == 2:
            new.append(path_tmp)
    else:
        spaces = ' ' * max(get_terminal_size().columns - 18, 0)
        print('  Download failed!' + spaces)
        fails.append(path_tmp)
    return (fails, new, upd, tot+leng, )


def dov(ov, fid):
    v.log_file.pvlog('  Downloading overview')
    print('  Downloading', fid+':', ov.name)
    return file_stream(ov.dl_link, ov.folder, ov.name, True)


def dfile(file, fid):
    v.log_file.pvlog('  Downloading file')
    print('  Downloading', fid+':', file.name)
    return file_stream(file.dl_link, file.folder, file.name)


def file_stream(link, folder, name, ov=False):
    with v.se.get(link, stream=True) as req:
        if ov and req.status_code >= 500:
            # Probably DNE
            v.log_file.pvlog('  File does not exist!')
            return (True, '', 0, )
        if req.status_code >= 400:
            # Unsuccessful request
            v.log_file.pvlog('  File cannot be downloaded!')
            return (False, '', 0, )
        return write_file(req, folder, name)


def write_file(req, folder, name):
    # Create folder recursively
    tmp_folder = os.path.join(cdirs['tmp_folder'], folder)
    Path(tmp_folder).mkdir(parents=True, exist_ok=True)
    ext, leng = get_ext_len(req)
    leng /= cs
    ext = '.' + ext if ext else ''
    file = os.path.join(tmp_folder, name+ext)
    # Download
    with open(file, 'wb') as f:
        prog_bar(f, name+ext, leng, req)
    return (True, ext, leng, )


def get_ext_len(req):
    headers = req.headers
    if 'Content-Disposition' in headers and 'Content-Length' in headers:
        cd = headers['Content-Disposition']
        name_mat = search(r'filename=\"(.+)\"', cd)
        if name_mat:
            name = unquote(name_mat[1])
            # Primitive extension. Can be wrong (e.g., .tar.gz)
            return (name.split('.')[-1], int(headers['Content-Length']), )
    return ('', 0, )


def prog_bar(f, name, leng, req):
    finished = 0
    s_leng = '{:.3f}'.format(leng)
    len_s = len(s_leng)
    len_end = 2 * len_s + 15
    len_name = len(name)
    for chunk in req.iter_content(chunk_size=cs):
        if chunk:
            width = get_terminal_size().columns - 2
            # Format: Filename [######] (downloaded/total MiB:percent%)
            if width >= len_end:
                # Print if only the final bit can be held
                finished += len(chunk) / cs
                percent = finished / leng * 100
                s_fin = '{:.3f}'.format(finished).rjust(len_s)
                s_per = '{:6.2f}'.format(percent)
                s_end = '(' + s_fin + '/' + s_leng + ' MiB:' + s_per + '%)'
                width -= len_end + 1
                if width <= 0:
                    print(' ', s_end, end='\r')
                    continue
                if width < len_name:
                    # Print partial filename
                    print(' ', name[:width], s_end, end='\r')
                    continue
                # Print full filename
                width -= len_name + 4
                if width <= 0:
                    print(' ', name, s_end, end='\r')
                    continue
                per_char = 100 / width
                hashes = int(percent / per_char)
                n = int(ceil(10*(percent/per_char-hashes)))
                str_hashes = '#' * hashes
                str_num = '' if n == 0 else '#' if n == 10 else str(n)
                str_dots = '.' * (width - hashes - 1)
                prog = '[' + str_hashes + str_num + str_dots + ']'
                print(' ', name, prog, s_end, end='\r')
            f.write(chunk)

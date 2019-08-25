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
    '''Main download function

    Args:
        ovs   (List[Overview]): List of `Overview` objects
        files (List[File])    : List of `File` objects
    '''
    v.log_file.plog('-' * 24)
    v.log_file.plog('Downloading files...')
    fai = []                    # List of failed downloads
    new = []                    # List of new files
    upd = []                    # List of updated files
    tot = 0                     # Total file size
    tl = len(ovs) + len(files)  # Total file count
    fi = 0                      # File counter
    # Download overviews
    for ov in ovs:
        fi += 1
        tot = df(ov, fai, new, upd, tot, str(fi), str(tl), True)
    # Download files
    for file in files:
        fi += 1
        tot = df(file, fai, new, upd, tot, str(fi), str(tl), False)
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


def writes(cat, fn, arr):
    '''Print and write download status information of list of files to
      respective files

    Args:
        cat (str)      : Category to be listed
        fn  (str)      : Name of file to be written into
        arr (List[str]): List of file paths in the corresponding category
    '''
    fi = plur(len(arr), 'file')
    print(cat, f'(Detail in {fn}):', fi)
    with open(fn, 'w') as f:
        print(fi+':', file=f)
        if arr:
            for e in arr:
                vprint(' ', e.format(''))
                print(' ', e.format(''), file=f)
        else:
            vprint('  None')


def df(file, fai, new, upd, tot, fi, tl, ov):
    '''Download file :P

    Notes:
        The current file path will be added to one and ONLY one of `fai`,
          `new`, and `upd`

    Args:
        file (File)     : The file (can be `Overview`) object to be downloaded
        fai  (List[str]): List of paths for failed files (These files do not
                            exist)
        new  (List[str]): List of paths for new files
        upd  (List[str]): List of paths for updated files
        tot  (int)      : Total length of downloaded files so far
        fi   (str)      : File counter (This is the `fi`-th file)
        tl   (str)      : Total number of files
        ov   (bool)     : If the file object is `Overview`
    Returns:
        (int): Total length of downloaded files so far
    '''
    v.log_file.plog(' ', '-' * 18)
    # Create file progress text
    fid = fi.rjust(len(tl)) + '/' + tl
    # Try downloading file
    v.log_file.pvlog('  Downloading', 'overview' if ov else 'file')
    print('  Downloading', fid+':', file.name)
    succ, ext, leng = file_stream(file.dl_link, file.folder, file.name, ov)
    # Compose full filename and path
    file_tmp = file.name+'{}'+ext
    path_tmp = os.path.join(file.folder, file_tmp)
    # If download successful, try moving file
    if succ:
        suc_msg = ('  ' + file_tmp.format('')
                   + ' successfully downloaded! ({:.3f} MiB)'.format(leng))
        spaces = ' ' * max(get_terminal_size().columns - len(suc_msg), 0)
        print(suc_msg + spaces)
        # Try moving file
        stat = move_file(file.folder, path_tmp, file_tmp.format(r'-\d{14}'))
        print('  File moved!')
        if stat == 1:
            upd.append(path_tmp)
        elif stat == 2:
            new.append(path_tmp)
    # If download unsuccessful, print and add to list of failures
    else:
        spaces = ' ' * max(get_terminal_size().columns - 18, 0)
        print('  Download failed!' + spaces)
        fai.append(path_tmp)
    return tot+leng


def file_stream(link, folder, name, ov):
    '''Try setting up the file stream for the file to be downloaded

    Args:
        link   (str) : File download link
        folder (str) : File folder path
        name   (str) : File name w/o extension
        ov     (bool): If the file object is `Overview`
    Returns:
        (bool): If downloading is successful
        (str) : File extension
        (int) : File length
    '''
    with v.se.get(link, stream=True) as req:
        # Overviews can be nonexistent depending on the course. 500s can
        #   indicate a DNE. Totally normal
        if ov and req.status_code >= 500:
            v.log_file.pvlog('  File does not exist!')
            return (False, '', 0)
        # 400s indicate a non-downloadable file. Probably a link, webpage, etc.
        if req.status_code >= 400:
            # Unsuccessful request
            v.log_file.pvlog('  File cannot be downloaded!')
            return (False, '', 0)
        # The file should be able to be downloaded
        return (True, *write_file(req, folder, name))


def write_file(req, folder, name):
    '''Write content to file

    Args:
        req    (Response): Response object from download request
        folder (str)     : File folder path
        name   (str)     : File name w/o extension
    Returns:
        (str): File extension
        (int): File length
    '''
    # Create folder recursively
    tmp_folder = os.path.join(cdirs['tmp_folder'], folder)
    Path(tmp_folder).mkdir(parents=True, exist_ok=True)
    # Get file extension and length and construct file name
    ext, leng = get_ext_len(req)
    leng /= cs
    name += ext
    file = os.path.join(tmp_folder, name)
    # Download and write to file
    with open(file, 'wb') as f:
        prog_bar(f, name, leng, req)
    return (ext, leng)


def get_ext_len(req):
    '''Get file extension and length from request response

    Args:
        req (Response): Response object from download request
    Returns:
        (str): File extension
        (int): File length
    '''
    headers = req.headers
    if 'Content-Disposition' in headers and 'Content-Length' in headers:
        # Search for file name
        name_mat = search(r'filename=\"(.+)\"', headers['Content-Disposition'])
        if name_mat:    # 584
            name = unquote(name_mat[1])
            # Primitive extension. Can be wrong (e.g., .tar.gz)
            return (f'.{name.split(".")[-1]}', int(headers['Content-Length']))
    return ('', 0)


def prog_bar(f, name, leng, req):
    '''Write content to file while displaying progress bar

    Args:
        f    (BinaryFile): File object to be written to
        name (str)       : File name with extension
        leng (float)     : File length in MiB
        req  (Response)  : Response object from download request
    '''
    finished = 0                # Amount finished in MiB
    s_leng = f'{leng:.3f}'      # File length in MiB formatted as 3 decimals
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
                s_fin = f'{finished:.3f}'.rjust(len_s)
                s_per = f'{percent:6.2f}'
                s_end = f'({s_fin}/{s_leng} MiB:{s_per}%)'
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
                prog = f'[{str_hashes}{str_num}{str_dots}]'
                print(' ', name, prog, s_end, end='\r')
            f.write(chunk)

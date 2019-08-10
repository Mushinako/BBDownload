#!/usr/bin/env python3
import sys
import os
import ctypes as c
from time import time
from shutil import rmtree

# Self-defined scripts
import v
from const import cdirs, cfiles, plur, clear_scr
from log import log_init
from local import setup, check
from url import get_urls
from down import down
from err import weird_err


HELP = '''
Please pin your courses that you would like to be downloaded.

When first run, this program will ask you for your credentials. You also need
a passphrase DIFFERENT from your CSULB password, to encrypt the latter in a
file named `data.json`. You will need this passphrase EVERY time you run this
program, as you need to decrypt your CSULB password every time for security
purposes.

All the contents will be written into `Contents` folder.

The same file will not be overwritten, but different files with the same
name (possibly different versions) will be renamed by attaching the time of
retrieval.

ARGUMENTS:
default           Refresh URLs and download contents
-h/--help         Show this text and exit program
-v/--verbose      Trigger for verbose terminal output
-r/--reset        Force reset. "data.json" will be deleted and you will need
                    to re-setup. You'll have to do this if you lose your
                    passphrase for this app
'''


def main():
    '''Main interface'''
    srt = time()    # Start time
    mid = 0         # Time after fetching all URLs
    end = 0         # Finish time
    try:
        # Initiate logs
        log_init()
        # Make folders
        make_folders()
        # Clear screen
        clear_scr()
        # Parse arguments
        help, reset, v.verbose = parse_args()
        # Print help
        if help:
            print(HELP)
            v.log_file.pvlog('Help printed')
            return
        # Reset or first use
        if reset or not os.path.isfile(cfiles['data_file']):
            setup()
        # Get passphrase and verify
        check()
        # Fetch URLs
        ovs, files = get_urls()
        mid = time()
        # Download files
        down(ovs, files)
    except Exception as e:
        # Uncaught error
        weird_err('General error', err=e)
    finally:
        end = time()
        # Remove temp folder
        temp = cdirs['tmp_folder']
        if os.path.isdir(temp):
            rmtree(temp)
        # Print time
        print('-' * 24)
        print('Total time:', *for_t(end-srt))
        if mid:
            print('  Fetch configurations:', *for_t(mid-srt))
            print('  Downloads           :', *for_t(end-mid))


def for_t(time):
    '''Convert seconds to minutes and seconds

    Args:
        time (float): The number of seconds
    Returns:
        (str): Properly pluralized minutes, in the form of \'\\d+ minutes?\'
        (str): Properly pluralized seconds, in the form of \'\\d+ seconds?\'
    '''
    m = int(time/60)
    s = round(time - m * 60, 3)
    return (plur(m, 'minute'), plur(s, 'second'))


def make_folders():
    '''Make necessary folders: data, temp, content'''
    # Make data folder
    dat = cdirs['data_folder']
    if os.path.isfile(dat):
        os.rename(dat, dat+'.bak')
    if not os.path.exists(dat):
        os.mkdir(dat)
    # Remove temp folder
    tmp = cdirs['tmp_folder']
    if os.path.exists(tmp):
        if os.path.isdir(tmp):
            rmtree(tmp)
            v.log_file.pvlog('Tmp folder detected and removed')
        else:
            os.rename(tmp, tmp+'.bak')
    # Make temp folder
    os.mkdir(tmp)
    if os.name == 'nt' and not c.windll.kernel32.SetFileAttributesW(tmp, 0x02):
        v.log_file.pvlog('Tmp folder not hidden')
    # Rename file with same name as contents folder
    cont = cdirs['cont_folder']
    if os.path.isfile(cont):
        os.rename(cont, cont+'.bak')


def parse_args():
    '''Parse arguments

    Returns:
        (bool): `help`?
        (bool): `reset`?
        (bool): `verbose`?
    '''
    v.log_file.pvlog('Args:', sys.argv)
    argv = sys.argv[1:]
    # User specified 'help'
    if '-h' in argv or '--help' in argv:
        return (True, False, False)
    argv = remove_all(argv, '-h', '--help')
    # User specified 'reset'
    reset = '-r' in argv or '--reset' in argv
    argv = remove_all(argv, '-r', '--reset')
    # User specified 'verbose'
    verbose = '-v' in argv or '--verbose' in argv
    argv = remove_all(argv, '-v', '--verbose')
    # Detect unknown args
    if argv:
        v.log_file.plog('Residual args:', argv)
        return (True, False, False)
    # Arg parsing successful
    return (False, reset, verbose)


def remove_all(arr, *s):
    '''Returns an list with elements except those specified

    Args:
        arr (List[str]): List of elements to be checked
        s   (List[str]): List of elements to be excluded
    Returns:
        (List[str]): List without excluded elements
    '''
    return [x for x in arr if x not in s]

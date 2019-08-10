#!/usr/bin/env python3
import re
import traceback
from sys import exit
from shutil import rmtree
from json import loads
from os.path import isdir
from json.decoder import JSONDecodeError

# Self-defined scripts
import v
from const import cdirs


def g_err(code, e_text, w_text, *msg, add=None, err=None):
    '''General error

    Args:
        code   (int)        : Error code
        e_text (str)        : Main error text for logging (Shown to user if
                                `verbose`)
        w_text (str)        : More general-user-friendly version of error text,
                                shown to all users
        msg    (Tuple[str]) : List of extra messages for logging purposes
                                (Shown to user if `verbose`)
        add    (Tuple[str]) : List of additional messages to be shown to the
                                user
        err    (Error)      : Error object associated with the error
    '''
    v.log_file.pvlog('E:', e_text)
    for m in msg:
        v.log_file.pvlog(m)
    if err is not None:
        v.log_file.pvlog(traceback.format_exc())
        v.log_file.pvlog(err)
    v.log_file.plog(w_text)
    if add is not None:
        for a in add:
            v.log_file.plog(a)
    temp = cdirs['tmp_folder']
    if isdir(temp):
        rmtree(temp)
    exit(code)


def wrong_pass():
    '''Wrong passphrase error (ERRNO 2)'''
    g_err(2, 'Passphrase not match', 'Wrong passphrase!')


def login_chk(login):
    '''Invalid login check (ERRNO 3)

    Args:
        login (bytes): Login page content
    Returns:
        (Dict): Key-value pairs for tokens
    '''
    # Make token dictionary
    login_sto = {x[1].decode('utf-8'): x[2] for x in re.findall(
        br'localStorage\.setItem\(([\'"])([\w\.]+)\1,\1([\w\.]*)\1\)',
        login
    )}
    # No tokens found, error
    if login_sto is None:
        g_err(3, '\'login_sto\' regex error',
              'Cannot login. Check your CSULB credentials',
              add=('Try resetting by deleting \'data.json\'', ))
    return login_sto


def json_par(json, name, *msg, add=None):
    '''JSON parse check (ERRNO -1)

    Args:
        json (str)       : String to be parsed as JSON
        name (str)       : Identifier for debugging
        msg  (Tuple[str]): See `g_err()`
        add  (Tuple[str]): See `g_err()`
    Returns:
        (Dict): Parsed JSON
    '''
    try:
        return loads(json)
    except JSONDecodeError as e:
        g_err(-1, f'\'{name}\' JSON parse error', *msg, add=add, err=e)


def json_chk(key, json, *msg, name=None, add=None):
    '''JSON key check (ERRNO -2)

    Args:
        key  (str|int)   : Keys to be retrieved
        json (Dict)      : Parsed JSON
        msg  (Tuple[str]): See `g_err()`
        name (str)       : Identifier for debugging
        add  (Tuple[str]): See `g_err()`
    Returns:
        (str): Requested value
    '''
    try:
        return json[key]
    except KeyError as e:
        if name is None:
            name = key
        g_err(-2, f'{name} invalid key', 'JSON key error!', *msg, add=add,
              err=e)


def re_chk(regex, data, name, *msg, add=None):
    '''Regex search check (ERRNO -3)

    Args:
        regex (str|bytes): Regex, matching `data` type
        data  (str|bytes): Data to be searched
        name (str)       : Identifier for debugging
        msg  (Tuple[str]): See `g_err()`
        add  (Tuple[str]): See `g_err()`
    Returns:
        (Match): Match object for the search
    '''
    mat = re.search(regex, data)
    if mat is None:     # 562
        g_err(-3, f'\'{name}\' regex error', 'Regex parsing error!', *msg,
              add=add)
    return mat


def get_err(name, *msg, add=None):
    '''HTTP GET error (ERRNO -4)

    Args:
        name (str)       : Identifier for debugging
        msg  (Tuple[str]): See `g_err()`
        add  (Tuple[str]): See `g_err()`
    '''
    g_err(-4, f'\'{name}\' get error', 'Fetching data error!', *msg, add=add)


def get_chk(url, name, *msg, err=True, add=None, **kwargs):
    '''HTTP GET check

    Args:
        url    (str)       : URL to which request will be sent
        name   (str)       : Identifier for debugging
        msg    (Tuple[str]): See `g_err()`
        err    (bool)      : Whether to raise error on a failed GET
        add    (Tuple[str]): See `g_err()`
        kwargs (Dict)      : See `requests`
    Returns:
        (bool)     : Success?
        (bytes|int): If successful, GET-returned content; else, status code
    '''
    req = v.se.get(url, **kwargs)
    stat = req.status_code
    if stat >= 300:     # 562
        if err:
            get_err(name, *msg, add=None)
        return (False, stat)
    return (True, req.content)


def post_chk(url, data, name, *msg, err=True, add=None, **kwargs):
    '''HTTP POST check (ERRNO -5)

    Args:
        url    (str)       : URL to which request will be sent
        data   (Dict)      : POST data body
        name   (str)       : Identifier for debugging
        msg    (Tuple[str]): See `g_err()`
        err    (bool)      : Whether to raise error on a failed GET
        add    (Tuple[str]): See `g_err()`
        kwargs (Dict)      : See `requests`
    Returns:
        (bool)     : Success?
        (bytes|int): If successful, POST-returned content; else, status code
    '''
    req = v.se.post(url, data, **kwargs)
    stat = req.status_code
    if stat >= 300:     # 562
        if err:
            g_err(-5, f'\'{name}\' post error', 'Posting data error!', *msg,
                  add=add)
        return (False, stat)
    return (True, req.content)


def weird_err(msg, *msgs, add=None, err=None):
    '''Unknown error (ERRNO -99)

    Args:
        msg  (str)       : Main error text for logging (Shown to user if
                             `verbose`)
        msgs (Tuple[str]): List of extra messages for logging purposes (Shown
                             to user if `verbose`)
        add  (Tuple[str]): List of additional messages to be shown to the user
        err  (Error)     : Error object associated with the error
    '''
    g_err(-99, msg, 'Unexpected error!', *msgs, add=add, err=err)

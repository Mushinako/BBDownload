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
    g_err(2, 'Passphrase not match', 'Wrong passphrase!')


def login_chk(login):
    login_sto = {x[1].decode('utf-8'): x[2] for x in re.findall(
        br'localStorage\.setItem\(([\'"])([\w\.]+)\1,\1([\w\.]*)\1\)',
        login
    )}
    if login_sto is None:
        g_err(3, '\'login_sto\' regex error',
              'Cannot login. Check your CSULB credentials',
              add=('Try resetting by deleting \'data.json\'', ))
    return login_sto


def json_chk(key, json, *msg, name=None, mul=False, par=True, add=None):
    try:
        if par:
            json = loads(json)
        if mul:
            ret = [json[k] for k in key]
        else:
            ret = json[key]
    except (KeyError, JSONDecodeError) as e:
        if name is None:
            name = ' & '.join(key)
        g_err(-1, name+' invalid key', 'JSON key error!', *msg, add=add, err=e)
    else:
        return ret


def re_chk(regex, data, name, *msg, comp=True, add=None):
    if compile:
        mat = re.search(regex, data)
    else:
        mat = regex.search(data)
    if mat is None:
        g_err(-2, '\''+name+'\' regex error', 'Regex parsing error!', *msg,
              add=add)
    return mat


def get_err(name, *msg, add=None):
    g_err(-3, name+' get error', 'Fetching data error!', *msg, add=add)


def get_chk(url, name, *msg, err=True, add=None, **kwargs):
    req = v.se.get(url, **kwargs)
    stat = req.status_code
    if stat >= 300:     # 562
        if err:
            get_err(name, *msg, add=None)
        return (False, stat)
    return req.content if err else (True, req.content)


def post_chk(url, data, name, *msg, err=True, add=None, **kwargs):
    req = v.se.post(url, data, **kwargs)
    stat = req.status_code
    if stat >= 300:     # 562
        if err:
            g_err(-4, name+' post error', 'Posting data error!', *msg, add=add)
        return (False, stat)
    return req.content if err else (True, req.content)


def weird_err(msg, *msgs, add=None, err=None):
    g_err(-99, msg, 'Unexpected error!', *msgs, add=add, err=err)

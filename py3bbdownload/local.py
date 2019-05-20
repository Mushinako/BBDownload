#!/usr/bin/env python3
from json import loads, dumps
from getpass import getpass

# Self-defined scripts
import v
from const import cfiles
from pswd import check_pp, create_pp


def setup():
    v.log_file.pvlog('-'*20)
    v.log_file.pvlog('Start setup')
    # Get passphrase
    hash, cipher = create_pp()
    # Get credentials
    id = cipher.encrypt(input('Your CSULB ID: ')).decode('utf-8')
    v.log_file.log('ID obtained')
    pw = cipher.encrypt(getpass('Your CSULB password: ')).decode('utf-8')
    v.log_file.log('Password obtained')
    # Write credentials
    data = dumps({'hash': hash.decode('utf-8'), 'id': id, 'pw': pw, })
    with open(cfiles['data_file'], 'w') as f:
        print(data, file=f)
    v.log_file.pvlog('Credentials written to \'data.json\'')
    v.log_file.plog('Setup successful!')


def check():
    v.log_file.pvlog('-'*20)
    v.log_file.pvlog('Checking passphrase')
    with open(cfiles['data_file']) as f:
        data = loads(f.read())
    # Prompt for passphrase
    cipher = check_pp(data['hash'].encode('utf-8'))
    v.clogin_info['userName'] = cipher.decrypt(data['id'])
    v.clogin_info['password'] = cipher.decrypt(data['pw'])
    v.log_file.plog('Credentials decrypted!')

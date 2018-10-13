#!/usr/bin/env python3
import os
import sys
import base64
import hashlib
import bcrypt
import getpass
from Crypto import Random
from Crypto.Cipher import AES

import defconst


class AESCipher:
    def __init__(self, key):
        self.key = hashlib.sha256(key).digest()

    def encrypt(self, data):
        iv = Random.new().read(AES.block_size)
        c = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + c.encrypt(self._pad(data).encode('utf-8')))

    def decrypt(self, data):
        data = base64.b64decode(data)
        c = AES.new(self.key, AES.MODE_CBC, data[:AES.block_size])
        return self._unpad(c.decrypt(data[AES.block_size:])).decode('utf-8')

    def _pad(self, data):
        k = AES.block_size - len(data) % AES.block_size
        return data + k * chr(k)

    @staticmethod
    def _unpad(data):
        return data[:-data[-1]]


# Check if Password is Correct
def check_pw(pw_hash):
    pw = getpass.getpass('Decrypt Your Credentials: ').encode('utf-8')
    hashed = pw_hash.encode('utf-8')
    print()

    if hashed == bcrypt.hashpw(pw, hashed):
        return pw
    else:
        print('Password No Match!')
        print('Make Sure You Use the Password Set Up in This App!')
        sys.exit()


# Create and Return Cipher
def create_cipher():
    if defconst.cipher is None:
        defconst.cipher = AESCipher(check_pw(defconst.data['hash']))


# Create Password
def create_pw():
    while True:
        pw1 = getpass.getpass((
            'Inputed Password won\'t Show for Security Reasons.'
            'Keep Typing and Hit Enter When You Finish.\n'
            'Think of a Password to Encrypt Your Login Crendentials: '
        )).encode('utf-8')
        hashed = bcrypt.hashpw(pw1, bcrypt.gensalt())

        pw2 = getpass.getpass(
            'Now Think of That Password Again: '
        ).encode('utf-8')

        # If Passwords Match, Yay!
        if hashed == bcrypt.hashpw(pw2, hashed):
            print('Password Set up!\n')
            defconst.cipher = AESCipher(pw2)
            return hashed
        print('Password No Match!\n')
        os.system('cls' if os.name == 'nt' else 'clear')

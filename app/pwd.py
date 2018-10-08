#!/usr/bin/env python3
from sys import exit
from base64 import b64encode, b64decode
from hashlib import sha256
from Crypto import Random
from Crypto.Cipher import AES
from getpass import getpass
from bcrypt import hashpw


class AESCipher:
    def __init__(self, key):
        self.key = sha256(key).digest()

    def encrypt(self, data):
        iv = Random.new().read(AES.block_size)
        c = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + c.encrypt(self._pad(data).encode('utf-8')))

    def decrypt(self, data):
        data = b64decode(data)
        c = AES.new(self.key, AES.MODE_CBC, data[:AES.block_size])
        return self._unpad(c.decrypt(data[AES.block_size:])).decode('utf-8')

    def _pad(self, data):
        k = AES.block_size - len(data) % AES.block_size
        return data + k * chr(k)

    @staticmethod
    def _unpad(data):
        return data[:-data[-1]]


def check_pw(pw_hash):
    pw = getpass().encode('utf-8')
    hashed = pw_hash.encode('utf-8')
    print()

    if hashed == hashpw(pw, hashed):
        return pw
    else:
        print('Password no match!')
        print('Make sure you use the password set up in this app!')
        exit()

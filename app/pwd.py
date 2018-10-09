#!/usr/bin/env python3
import sys
import base64
import hashlib
import bcrypt
from getpass import getpass
from Crypto import Random
from Crypto.Cipher import AES


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


def check_pw(pw_hash):
    pw = getpass().encode('utf-8')
    hashed = pw_hash.encode('utf-8')
    print()

    if hashed == bcrypt.hashpw(pw, hashed):
        return pw
    else:
        print('Password no match!')
        print('Make sure you use the password set up in this app!')
        sys.exit()

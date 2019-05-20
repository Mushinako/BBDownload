#!/usr/bin/env python3
import os
import bcrypt
from time import sleep
from subprocess import call
from hashlib import sha256
from getpass import getpass
from base64 import b64encode, b64decode
from Crypto import Random
from Crypto.Cipher import AES

# Self-defined scripts
import v
from err import wrong_pass


class AESC:
    def __init__(self, key):
        # The actual key is a sha256 of input
        self._key = sha256(key).digest()
        self._bs = AES.block_size
        self._mode = AES.MODE_CBC

    def encrypt(self, data):
        iv = Random.new().read(self._bs)
        c = AES.new(self._key, self._mode, iv)
        return b64encode(iv + c.encrypt(self._pad(data).encode('utf-8')))

    def decrypt(self, data):
        d = b64decode(data)
        c = AES.new(self._key, self._mode, d[:self._bs])
        return self._unpad(c.decrypt(d[self._bs:])).decode('utf-8')

    def _pad(self, data):
        k = self._bs - len(data) % self._bs
        return data + k * chr(k)

    @staticmethod
    def _unpad(data):
        return data[:-data[-1]]


# Create passphrase
def create_pp():
    for _ in range(3):
        print('The password won\'t show for security reasons.')
        print('Keep typing and hit enter when you finish.')
        hash = bcrypt.hashpw(getpass('Passphrase: ').encode('utf-8'),
                             bcrypt.gensalt())
        pp = getpass('Verify passphrase: ').encode('utf-8')
        # Passphrase match, yay!
        if hash == bcrypt.hashpw(pp, hash):
            v.log_file.plog('Passphrase set up!')
            return (hash, AESC(pp))
        v.log_file.plog('W: Passphrase no match!')
        sleep(1)
        call('cls' if os.name == 'nt' else 'clear', shell=True)
    wrong_pass()


# Check passphrase
def check_pp(hash):
    call('cls' if os.name == 'nt' else 'clear', shell=True)
    pp = getpass('Check passphrase: ').encode('utf-8')
    if hash == bcrypt.hashpw(pp, hash):
        v.log_file.pvlog('Passphrase match!')
        return AESC(pp)
    wrong_pass()

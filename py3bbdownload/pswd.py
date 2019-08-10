#!/usr/bin/env python3
from time import sleep
from hashlib import sha256
from getpass import getpass
from bcrypt import hashpw, gensalt
from base64 import b64encode, b64decode
from Crypto import Random
from Crypto.Cipher import AES

# Self-defined scripts
import v
from const import clear_scr
from err import wrong_pass


class AESC:
    '''Defines AES cipher objects

    Attributes:
        _key  (bytes): AES key
        _bs   (int)  : AES block size (default 16)
        _mode (int)  : AES mode (default 2 for CBC)
    '''

    def __init__(self, key):
        '''Creates AES cipher object

        Note:
            The actual key for AES is a sha256 hash of the user input. This
            is used to merely satisfy AES key requirement, and does NOT
            strengthen a weak passphrase

        Args:
            key (bytes): User inputted key
        '''
        # The actual key is a sha256 of input
        self._key = sha256(key).digest()
        self._bs = AES.block_size
        self._mode = AES.MODE_CBC

    def encrypt(self, data):
        '''Encrypts data specified

        Args:
            data (str): Data to be encrypted
        Returns:
            (bytes): Base64-encoded encrypted data
        '''
        iv = Random.new().read(self._bs)
        c = AES.new(self._key, self._mode, iv)
        return b64encode(iv + c.encrypt(self._pad(data).encode('utf-8')))

    def decrypt(self, data):
        '''Decrypts data specified

        Args:
            data (str): Base64-encoded data to be decrypted
        Returns:
            (str): Decrypted data
        '''
        d = b64decode(data)
        c = AES.new(self._key, self._mode, d[:self._bs])
        return self._unpad(c.decrypt(d[self._bs:])).decode('utf-8')

    def _pad(self, data):
        '''Pad string

        Args:
            data (str): Data to be padded
        Returns:
            (str): Padded data
        '''
        k = self._bs - len(data) % self._bs
        return data + k * chr(k)

    @staticmethod
    def _unpad(data):
        '''Remove padding

        Args:
            data (bytes): Padded data
        Returns:
            (bytes): Unpadded data
        '''
        return data[:-data[-1]]


def create_pp():
    '''Create passphrase
    Prompt user for passphrase until success, or 3 failures

    Returns:
        (bytes): Hashed passphrase
        (AESC) : AES Cipher object with designated passphrase
    '''
    for _ in range(3):
        print('The password won\'t show for security reasons.')
        print('Keep typing and hit enter when you finish.')
        hash = hashpw(getpass('Passphrase: ').encode('utf-8'), gensalt())
        pp = getpass('Verify passphrase: ').encode('utf-8')
        # Check passphrase match
        if hash == hashpw(pp, hash):
            v.log_file.plog('Passphrase set up!')
            return (hash, AESC(pp))
        v.log_file.plog('W: Passphrase no match!')
        sleep(1)
        clear_scr()
    wrong_pass()


def check_pp(hash):
    '''Check passphrase

    Args:
        hash (bytes): Hashed passphrase to compare with user input
    '''
    clear_scr()
    pp = getpass('Check passphrase: ').encode('utf-8')
    if hash == hashpw(pp, hash):
        v.log_file.pvlog('Passphrase match!')
        return AESC(pp)
    wrong_pass()

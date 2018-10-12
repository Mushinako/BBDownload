#!/usr/bin/env python3
import os
import hashlib
from hashlib import md5, sha1


class FileData:
    def __init__(self, path):
        self.path = path
        self.size = os.stat(path).st_size
        self.hashes = None

    def hash(self):
        m = hashlib.md5()
        s = hashlib.sha1()
        with open(self.path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                m.update(data)
                s.update(data)
        self.hashes = [m.hexdigest(), s.hexdigest()]

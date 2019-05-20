#!/usr/bin/env python3
import os

# Self-defined scripts
import v
from const import cdirs, time


class LogFile:
    def __init__(self, log_fn):
        self._log_fn = log_fn
        # Write disclaimer and primitive info
        self.log('This log file does NOT include your ID, password, or',
                 'passphrase. These are not automatically uploaded. Too lazy',
                 sep='\n')
        self.log()
        self.log('OS NAME:', os.name)

    def log(self, *args, **kwargs):
        with open(self._log_fn, 'a') as f:
            print(*args, file=f, **kwargs)

    def plog(self, *args, **kwargs):
        self.log(*args, **kwargs)
        print(*args, **kwargs)

    def pvlog(self, *args, **kwargs):
        self.log(*args, **kwargs)
        if v.verbose:
            print(*args, **kwargs)


# Initiate log
def log_init():
    log_folder = cdirs['log_folder']
    if not os.path.isdir(log_folder):
        if os.path.exists(log_folder):
            os.rename(log_folder, log_folder + '.bak')
        os.mkdir(log_folder)
    log_fn = os.path.join(log_folder, time+'.log')
    v.log_file = LogFile(log_fn)


def vprint(*args, **kwargs):
    if v.verbose:
        print(*args, **kwargs)

#!/usr/bin/env python3
import os

# Self-defined scripts
import v
from const import cdirs, time


class LogFile:
    '''Defines LogFile objects

    Attributes:
        _log_fn (str): Path of log file
    '''

    def __init__(self, log_fn):
        '''Creates LogFile object and initialize first few lines

        Args:
            log_fn (str): Path of log file
        '''
        self._log_fn = log_fn
        # Write disclaimer and primitive info
        self.log('This log file does NOT include your ID, password, or',
                 'passphrase. These are not automatically uploaded. Too lazy',
                 sep='\n')
        self.log()
        self.log('OS NAME:', os.name)

    def log(self, *args, **kwargs):
        '''Log content to log file

        Args:
            args   (Tuple): See `print()`
            kwargs (Dict) : See `print()`
        '''
        with open(self._log_fn, 'a') as f:
            print(*args, **kwargs, file=f)

    def plog(self, *args, **kwargs):
        '''Log content to log file and print the content on the screen

        Args:
            args   (Tuple): See `print()`
            kwargs (Dict) : See `print()`
        '''
        self.log(*args, **kwargs)
        print(*args, **kwargs)

    def pvlog(self, *args, **kwargs):
        '''Log content to log file and, if `verbose`, print the content on the
          screen

        Args:
            args   (Tuple): See `print()`
            kwargs (Dict) : See `print()`
        '''
        self.log(*args, **kwargs)
        vprint(*args, **kwargs)


def log_init():
    '''Initiate log file'''
    log_folder = cdirs['log_folder']
    # Make log folder, if not exists; rename any file with the same name
    if not os.path.isdir(log_folder):
        if os.path.exists(log_folder):
            os.rename(log_folder, log_folder + '.bak')
        os.mkdir(log_folder)
    # Make log file
    log_fn = os.path.join(log_folder, time+'.log')
    v.log_file = LogFile(log_fn)


def vprint(*args, **kwargs):
    '''If `verbose`, print the content on the screen

    Args:
        args   (List): See `print()`
        kwargs (Dict): See `print()`
    '''
    if v.verbose:
        print(*args, **kwargs)

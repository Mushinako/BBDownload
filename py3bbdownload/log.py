#!/usr/bin/env python3
log_file = None

def print_log(*args, sep=' ', end='\n'):
    a = [str(arg) for arg in args]
    log_file.write(sep.join(a)+end)
    log_file.flush()
    print(*a, sep=sep, end=end)

def log(*args, sep=' ', end='\n'):
    log_file.write(sep.join([str(a) for a in args])+end)
    log_file.flush()

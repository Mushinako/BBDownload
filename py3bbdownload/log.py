#!/usr/bin/env python3
log_file = None

def print_log(*args, sep=' ', end='\n'):
    log_file.write(sep.join(args)+end)
    log_file.flush()
    print(*args, sep=sep, end=end)

def log(*args, sep=' ', end='\n'):
    log_file.write(sep.join(args)+end)
    log_file.flush()

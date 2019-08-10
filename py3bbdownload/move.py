#!/usr/bin/env python3
import os
from re import fullmatch
from shutil import move
from filecmp import cmp
from pathlib import Path

# Self-defined scripts
import v
from const import cdirs, time
from log import vprint


def move_file(folder, path_tmp, regex):
    '''Move file and merge/rename

    Args:
        folder   (str):
        path_tmp (str):
        regex    (str):
    Returns:
        (int): Return code (0: duplicate; 1: updated; 2: new)
    '''
    v.log_file.pvlog('   ', '-' * 15)
    v.log_file.pvlog('    Moving file')
    # Temporary and final paths
    rel_path = path_tmp.format('')
    print('  Moving', rel_path)
    tmp_path = os.path.join(cdirs['tmp_folder'], rel_path)
    cont_folder = os.path.join(cdirs['cont_folder'], folder)
    cont_path = os.path.join(cdirs['cont_folder'], path_tmp.format('-'+time))
    Path(cont_folder).mkdir(parents=True, exist_ok=True)
    # Check duplicates
    dup_files = [f for f in os.listdir(cont_folder)
                 if fullmatch(regex, f) is not None]
    # If no dup_files, then it is a new file
    if not dup_files:
        vprint('  New file!')
        move(tmp_path, cont_path)
        return 2
    # Only compare with last
    cur_path = os.path.join(cont_folder, sorted(dup_files)[-1])
    if cmp(tmp_path, cur_path, shallow=False):
        # The files are the same
        vprint('  Duplicate!')
        return 0
    # New version
    move(tmp_path, cont_path)
    vprint('  New file version!')
    return 1

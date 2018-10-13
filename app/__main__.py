import os
import sys
import shutil
import zipfile


import fetch_config
import fetch_files
import conf_setup


def main(): # TODO: Other implementations
    HELP = '''
    This project is distributed under GPLv3 by Mushinako. This project comes
    with absolutely NO warranty, and I am NOT responsible for any data loss
    and/or leak. Please only test this script if you understand what you and
    this script are doing!

    This short script grabs all files from BeachBoard @ CSULB (hopefully),
    unless the system breaks (which occurs often) or have some major changes.

    This program needs to be setup at the first time, asking you for your
    credentials, and a file named "data.json" should appear in data/, storing
    necessary data. [This file will refresh once every 5 times the program is
    run. (FUTURE)]

    You also need a password, ideally different from your CSULB password, to
    encrypt the latter in the file. You will need this password EVERY time you
    run this program, as you need to decrypt your CSULB password every time.

    The same file will not be overwritten, but different files with the same
    name (possibly different versions) will be renamed by attaching " (1)",
    " (2)", etc.

    ARGUMENTS:
    -h, --help      Show this text
    -c, --course    Refresh course URLs. You may likely have to do this every
                    time the instructor changes anything on BB
    -r, --reset     Force reset. "data.json" will be deleted and you will
                    need to re-setup. You'll have to do this if you lose your
                    passphrase for this app.
    '''

    os.system('cls' if os.name == 'nt' else 'clear')

    if len(sys.argv) == 1:
        if os.path.isfile('data/data.json'):
            if os.path.isdir('Temp'):
                shutil.rmtree('Temp')

            try:
                fetch_config.fetch_config(True)
                fetch_files.fetch_files()

            except Exception as e:
                print(e)
                if os.path.isdir('Contents'):
                    shutil.rmtree('Contents')

            finally:
                if os.path.isdir('Temp'):
                    shutil.rmtree('Temp')
                print()

        else:
            print('Configuration Data not Found')
            print('Setting up...')
            conf_setup.setup(False)

    elif sys.argv[1] in ['-h', '--help']:
        print(HELP)

    elif sys.argv[1] in ['-c', '--course']:
        conf_setup.setup(os.path.isfile('data/data.json'))

    elif sys.argv[1] in ['-r', '--reset']:
        conf_setup.setup(False)

    else:
        raise ValueError('Invalid arguments! Use \'-h\' for help!')


if __name__ == '__main__':
    main()

import os
import sys
import shutil
import pathlib
import time
import fetch_config
import fetch_files
import fetch_grades
import conf_setup
import log as l


def fetch_content():
    if os.path.isfile('data/data.json'):
        if os.path.isdir('.temp'):
            shutil.rmtree('.temp')
        try:
            fetch_config.fetch_config(True)
            fetch_files.fetch_files()
        except Exception as e:
            l.print_log('General exception occurred!')
            l.print_log(e)
        finally:
            if os.path.isdir('.temp'):
                shutil.rmtree('.temp')
            print()
            return
    l.print_log('Configuration Data not Found')
    l.print_log('Setting up...\n')
    conf_setup.setup(False)


def main():  # TODO: Other implementations
    HELP = '''
    This project is distributed under GPLv3 by Mushinako. This project comes
      with absolutely NO warranty, and I am NOT responsible for any data loss
      and/or leak. Please only test this script if you understand what you and
      this script are doing!

    This short script grabs all files from BeachBoard @ CSULB (hopefully),
      unless the system breaks (which occurs often) or have some major changes.

    When first run, this program will ask you for your credentials, and a file
      named "data.json" should appear in "data" folder, storing necessary data.

    You also need a password, ideally different from your CSULB password, to
      encrypt the latter in the file. You will need this password EVERY time you
      run this program, as you need to decrypt your CSULB password every time.

    All the contents and grades will be written into "Contents" folder.

    The same file will not be overwritten, but different files with the same
      name (possibly different versions) will be renamed by attaching " (1)",
      " (2)", etc.

    ARGUMENTS:
      default               Refresh the URLs and download contents
      -h/--help             Show this text
      -c/--course           Do not refresh course URLs. If the instructor
                              changes anything on BeachBoard, the URL would
                              change. This app defaults to refreshing the URLs
                              each time. Use this option to disable such
                              behavior.
      -r/--reset            Force reset. "data.json" will be deleted and you
                              will need to re-setup. You'll have to do this if
                              you lose your passphrase for this app

    This program can only accept 1 argument. Any argument other than the first
      one will be ignored
    '''

    # Make Log Folder if not exists
    LOG_FOLDER_PATH = os.path.join('Debug', 'Logs')
    pathlib.Path(LOG_FOLDER_PATH).mkdir(exist_ok=True)
    with open(os.path.join(LOG_FOLDER_PATH, f'{str(int(time.time()))}.log'),
              'w') as l.log_file:
        l.log('This log file includes your system type, your arguments,')
        l.log('file names, sizes, and hashes in \'Contents\' folder, and')
        l.log('all program outputs, all which may help debug any problems')
        l.log('that may occur. It does NOT record any ID\'s, passwords, or')
        l.log('PINs. These logs are also never automatically uploaded, as I')
        l.log('do not want to rent a server for this thing.')
        l.log()
        l.log(f'OS NAME: {os.name}')
        l.log(f'ARGS: {str(sys.argv)}')
        os.system('cls' if os.name == 'nt' else 'clear')
        if len(sys.argv) == 1:
            conf_setup.setup(os.path.isfile('data/data.json'))
            fetch_content()
            return
        if sys.argv[1] in ['-h', '--help']:
            print(HELP)
            return
        if sys.argv[1] in ['-c', '--course']:
            fetch_content()
            return
        if sys.argv[1] in ['-r', '--reset']:
            conf_setup.setup(False)
            return
        l.print_log('Invalid arguments! Use \'-h\' for help!')


if __name__ == '__main__':
    main()

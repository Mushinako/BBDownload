import os
import sys
import shutil
import fetch_config
import fetch_files
import fetch_grades
import conf_setup


def fetch_content():
    if os.path.isfile('data/data.json'):
        if os.path.isdir('.temp'):
            shutil.rmtree('.temp')
        try:
            fetch_config.fetch_config(True)
            fetch_files.fetch_files()
        except Exception as e:
            print(e)
        finally:
            if os.path.isdir('.temp'):
                shutil.rmtree('.temp')
            print()
            return
    print('Configuration Data not Found')
    print('Setting up...\n')
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

    os.system('cls' if os.name == 'nt' else 'clear')
    if len(sys.argv) == 1:
        conf_setup.setup(os.path.isfile('data/data.json'))
        fetch_content()
        # fetch_grades.fetch_grades(1, False)
        return
    if sys.argv[1] in ['-h', '--help']:
        print(HELP)
        return
    if sys.argv[1] in ['-c', '--course']:
        fetch_content()
        # fetch_grades.fetch_grades(1, False)
        return
    if sys.argv[1] in ['-r', '--reset']:
        conf_setup.setup(False)
        return
    # TODO: Grades-related
    # if sys.argv[1] in ['-t', '--content']:
    #     fetch_content()
    #     return
    # if sys.argv[1] in ['-g', '--grade']:
    #     if len(sys.argv) > 3:
    #         if sys.argv[2] == 'csv':
    #             fetch_grades.fetch_grades(0, True)
    #             return
    #         if sys.argv[2] == 'md':
    #             fetch_grades.fetch_grades(1, True)
    #             return
    #         print('Wrong Grade Format!')
    #         return
    # if sys.argv[1] in ['-a', '--all']:
    #     if len(sys.argv) > 3:
    #         if sys.argv[2] == 'csv':
    #             fetch_content()
    #             fetch_grades.fetch_grades(0, False)
    #             return
    #         if sys.argv[2] == 'md':
    #             fetch_content()
    #             fetch_grades.fetch_grades(1, False)
    #             return
    #         print('Wrong Grade Format!')
    #         return
    print('Invalid arguments! Use \'-h\' for help!')


if __name__ == '__main__':
    main()
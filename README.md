#   bbdownload – BeachBoard Content Downloader
This short script grabs all files from BeachBoard @ CSULB (hopefully),
unless the system breaks (which occurs often) or have some major changes.

##  License
This project is distributed under GPLv3 by Mushinako. This project comes
with absolutely NO warranty, and I am NOT responsible for any data loss
and/or leak. I'm not an expert on data security (though trying to be).
Please only test this script if you understand what you and this script
are doing!

##  Usage
On Windows:
- Double-click on `app.bat` or run `.\app.bat [-h|-c|-r]` from command line

On Mac OS/Linux:
- Make `app.sh` executable
- Double-click on `app.sh` or run `./app.sh [-h|-c|-r]` from terminal

Alternative:
- Use `python3 app [-h|-c|-r]` in this directory

**Please pin your courses that you would like to be downloaded.**

This program needs to be setup at the first time, asking you for your
credentials, and a file named "data.json" should appear in data/, storing
necessary data. ~~This file will refresh once every 5 times the program is
run. (FUTURE)~~

You also need a password, ideally different from your CSULB password, to
encrypt the latter in the file. You will need this password EVERY time you
run this program, as you need to decrypt your CSULB password every time.

The same file will not be overwritten, but different files with the same
name (possibly different versions) will be renamed by attaching " (1)",
" (2)", etc.

### Arguments
```
-h, --help      Show this text
-c, --course    Refresh course URLs. You may likely have to do this every
                time the instructor changes anything on BB
-r, --reset     Force reset. "data.json" will be deleted and you will
                need to re-setup. You'll have to do this if you lose your
                passphrase for this app.
```

##  Requirement
* Python 3.6+
* [pyCryptodome](https://www.pycryptodome.org/en/latest/index.html)
    * Install with `pip install pycryptodome` or `pip3 install pycryptodome`
* Necessary Credentials to Log into BeachBoard
* Other BB Configurations (Pin Your Courses!)
* Disk Space
* Enough Sanity to Bear the Bugs

##  Contributions!
Absolutely! File an issue and/or start a pull request! This project is likely
buggy, and supports are greatly welcomed!

#   bbdownload – BeachBoard Content Downloader
This short script grabs all files from BeachBoard @ CSULB (hopefully),
unless the system breaks (which occurs often) or have some major changes.

##  License
This project is distributed under GPLv3 by Mushinako. This project comes
with absolutely NO warranty, and I am NOT responsible for any data loss
and/or leak. I'm not an expert on data security (though trying to be).
~~Please only test this script if you understand what you and this script
are doing!~~ Do not test this script now as the setup procedure is not
completed yet!

##  Requirement
* Python 3.6+
* [pyCryptodome](https://www.pycryptodome.org/en/latest/index.html)
  * Install with `pip install pycryptodome` on Windows and
    `pip3 install pycryptodome` on other systems.

##  Usage
Click on `app.bat` or run `app.bat [-h|-r]` from command line if you're using
Windows. Use `python3 app.py [-h|-r]` on macOS or Linux.

Please pin your courses that you would like to be downloaded.

~~This program needs to be setup at the first time, asking you for your
credentials, and a file named "data.json" should appear, storing necessary
data for speedier login. This file will refresh once every 5 times the
program is run. (FUTURE)~~

You also need a password, ideally different from your CSULB password, to
encrypt the latter in the file. You will need this password EVERY time you
run this program, as you need to decrypt your CSULB password every time.

The same file will not be overwritten, but different files with the same
name (possibly different versions) will be renamed by attaching " (1)",
" (2)", etc.

### Arguments
```
-h, --help      Show help text
-r, --reset     Force reset. "data.json" will be deleted and you will
                need to re-setup.
```

##  Contributions!
Absolutely! File an issue and/or start a pull request! This project is not
finished yet, but supports are greatly welcomed!

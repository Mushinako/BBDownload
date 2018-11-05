#   BBDownload – BeachBoard Content Downloader
<!-- FIND THE GAME... -->
This short script grabs all files from BeachBoard @ CSULB (hopefully),
unless the system breaks (which occurs often) or have some major changes.


## Description
**Please pin your courses that you would like to be downloaded.**

When first run, this program will ask you for your credentials, and a file
  named "data.json" should appear in "data" folder, storing necessary data.

You also need a password, ideally different from your CSULB password, to
encrypt the latter in the file. You will need this password EVERY time you
run this program, as you need to decrypt your CSULB password every time.

All the contents and grades will be written into "Contents" folder.

The same file will not be overwritten, but different files with the same
name (possibly different versions) will be renamed by attaching " (1)",
" (2)", etc.


##  Usage
### On Windows:
- Double-click on `bbdownload.bat` or run `.\app.bat [-h|-c|-r]` from command
  line

### On Mac OS/Linux:
- Make `bbdownload.sh` executable (`chmod +x ./app.sh`)
- Open a terminal in this folder and run `./bbdownload.sh [-h|-c|-r]` from
  terminal

### Alternative:
- Use `python3 py3bbdownload [-h|-c|-r]` in this directory


## Arguments
```
default               Refresh the URLs and download contents and MD-formatted
                        grades
-h/--help             Show this text
-c/--course           Do not refresh course URLs. If the instructor changes
                        anything on BeachBoard, the URL would change. This app
                        defaults to refreshing the URLs each time. Use this
                        option to disable such behavior.
-r/--reset            Force reset. "data.json" will be deleted and you will
                        need to re-setup. You'll have to do this if you lose
                        your passphrase for this app
-t/--content          Download contents only
-a/--all [format]     Download contents and grades in selected format
```

### Formats
```
csv       Comma-separated values (Openable in Excel, LibreOffice Calc)
md        GitHub flavored markdown (Openable in text editors)
```

This program can only accept 1 argument. Any argument other than the first
  one will be ignored


##  Requirement
* Python 3.6+ (May work on 3.5 but I Cannot Guarantee)
* [pyCryptodome](https://www.pycryptodome.org/en/latest/index.html)
    * Install with `pip install pycryptodome` or `pip3 install pycryptodome`
* Necessary Credentials to Log into BeachBoard and Proper Settings
    * **Pin Your Courses!**
* Obviously, Internet Connection
* Disk Space
* Enough Sanity to Bear the Bugs


##  Future
* Download Grades Maybe?
* Print Changes

##  Contributions!
Absolutely! File an issue and/or start a pull request! This project is likely
buggy, and supports are greatly welcomed!


##  License
This project is distributed under GPLv3 by Mushinako. This project comes
with absolutely NO warranty, and I am NOT responsible for any data loss
and/or leak. I'm not an expert on data security (though trying to be).
**Please only test this script if you understand what you and this script
are doing!**

#   BBDownload – BeachBoard Content Downloader
<!-- FIND THE GAME... -->
This short script grabs all files from BeachBoard @ CSULB (hopefully),
unless the system breaks (which occurs often) or have some major changes.
**Please only test this script if you understand what you and this script
are doing!** This is a mere script to comply with my laziness to check BB.

##  Description
**Please pin your courses that you would like to be downloaded.**

When first run, this program will ask you for your credentials. You also need
a passphrase **different** from your CSULB password (e.g., `1234`, though not
recommended), to encrypt the latter in a file named `data.json` in `data`
folder. You will need this passphrase **every** time you run this program, as
you need to decrypt your CSULB password every time for security purposes.

All the contents will be written into `contents` folder.

The same file will not be overwritten, but different files with the same
name (possibly different versions) will be renamed by attaching the time of
retrieval.

##  Usage
### On Windows:
- Double-click on `bbdownload.bat` or run `.\bbdownload.bat [option]` from
  command line

### On macOS/Linux:
- Make `bbdownload` executable (`chmod +x ./bbdownload`) (Optional)
- Open a terminal in this folder and run `./bbdownload [option]` from
  terminal

### Alternative:
- Use `python3 py3bbdownload [option]` in this directory

##  Arguments
```
default           Refresh URLs and download contents
-h/--help         Show this text and exit program
-v/--verbose      Trigger for verbose terminal output
-r/--reset        Force reset. "data.json" will be deleted and you will need
                    to re-setup. You'll have to do this if you lose your
                    passphrase for this app
```

##  Requirement
### TL;DR
`pip3 install -r requirements.txt` or
`pip3 install requests bcrypt pycryptodome beautifulsoup4`

### Details
* Python 3.6+ (Recommended), may work on lower versions of Python 3
* [requests](https://2.python-requests.org/en/master/) (For web communications)
* [bcrypt](https://github.com/pyca/bcrypt/) (For passphrase verification)
* [pyCryptodome](https://www.pycryptodome.org/en/latest/index.html) (For
  personal data encryption)
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) (For HTML
  parsing)
* Necessary Credentials to log into BeachBoard and **pin your courses**!
* Obviously, internet connection
* Disk space
* Enough sanity to bear the bugs

It should also be noted that the files should not be opened during the running
of this script.

##  FAQ
Some FAQ can be found [here](./faq.md).

##  Contributions!
Absolutely, but why would you be interested in this? You are welcomed to file
an issue and/or start a pull request! This project is likely buggy, and
supports are greatly welcomed, and I do need to improve my skills as all of
mine are self-taught.

##  License
This project is distributed under [GPLv3](./LICENSE) by Mushinako. This project
comes with absolutely **NO** warranty, and I am **NOT** responsible for any
data loss and/or leak. I'm **NOT** an expert on data security.

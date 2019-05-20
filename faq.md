#   Frequently Asked Questions
##  Why some files fail to download?
These files are usually of specific types (e.g., links, embedded videos) that
are not immediately downloadable. If you believe that your file should be
downloadable (more obviously indicated as you can donwload it directly on the
website), then it's likely a bug.

##  It's sooooooo slow!
On average of my tests, the configurations take round 0.15 sec/file to search,
and increases roughly proportionally to the number of files. The download maxes
out around 0.5 MiB/s, which I will try to improve on in the future (not sure
how to yet. I may ditch streaming via `requests`). BB does not seem to offer
hashes for file comparisons, thus all files have to be downloaded and compared
locally.

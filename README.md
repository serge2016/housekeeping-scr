# housekeeping-scr

## memUsage.py

Monitors the process by PID and directory size by path, writes .log file with the following TAB-separated fields:
     - time, s
     - PID
     - available RAM, Gb
     - residen set size, Gb - the portion of RAM occupied by a process
     - % of total RAM occupied by a process, %
     - % of CPU used by a process.
     - size of given folder, Gb
     - free disk space on partition with given folder, Gb
     
OR plots the provided .log file.

Dependencies:
python:
 - psutil
 - subprocess
 - mathplotlib
 - pandas



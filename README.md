# memUsage.py

A python script that monitors a process by PID (with all subprocesses) and a directory size by path, writes .log file with the following TAB-separated fields:
- time, s
- PID
- available RAM, GB
- resident RAM size, GB (the portion of RAM occupied by a process)
- % of total RAM occupied by a process, %
- % of CPU used by a process, %
- size of given folder, GB
- free disk space on partition with given folder, GB

This script also allows to plot the provided .log file.

This script works with both python2 and python3.

Dependencies:
- psutil (always needed, tested for v5.6.1)
- mathplotlib (only when plotting .log files)
- pandas (only when plotting .log files)

For basic run only `psutil` package is needed (`pip install psutil` or `sudo apt install python-psutil`). Another way to install this package is:
```
wget -q "https://github.com/giampaolo/psutil/archive/release-5.6.3.tar.gz" -O "$HOME/psutil-release-5.6.3.tar.gz" \
&& tar -xzf "$HOME/psutil-release-5.6.3.tar.gz" \
&& cd "$HOME/psutil-release-5.6.3" \
&& python setup.py install \
&& cd "$HOME" \
&& rm -r "$HOME/psutil-release-5.6.3"
```

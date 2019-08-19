#!/usr/bin/python

# Authors: Olga I. Zolotareva, Sergey I. Mitrofanov
# LastUpdate: 19.08.2019 16:10.

from __future__ import print_function
import argparse
import sys, os
import psutil
import time
import subprocess


### argparse ###
parser = argparse.ArgumentParser(description="""Monitors the process by PID and directory size by path, writes .log file with the following TAB-separated fields:
     - time, s
     - PID
     - available RAM, Gb
     - residen set size, Gb - the portion of RAM occupied by a process
     - % of total RAM occupied by a process, %
     - % of CPU used by a process.
     - size of given folder, Gb
     - free disk space on partition with given folder, Gb

OR plots the provided logfile.
""" , formatter_class=argparse.RawTextHelpFormatter)

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--pid', dest='pid', type=int, help='PID to be watched. All children of this PID are watched too.', metavar='12345')
group.add_argument('--plot', dest='plot', help='Input file with log, generated by this script. This flag switches off log writing.', default=False, required=False, metavar='12345.log')
#group.add_argument('--pname', dest='pname', type=str, nargs=1, help='Process name, if no PID  provided.')
parser.add_argument('-o','--out', dest='out', type=str, help='Output filename without extention (.log). If no outfile name provided output will be written into file pid.log in current <dir>.', default='', required=False)
parser.add_argument('-d','--wdir', dest='wdir', type=str, help='Diretory to be watched (size).', default='.', required=False)
parser.add_argument('-t', '--time_step', dest='time_step', type=int, help='Write to logfile every N s. Default is 5s.', default=5, metavar='N')
parser.add_argument('--avail_mem', dest='avail_pmem', action='store_true', help='Plot free RAM (Gb) vs time (s).', default=False, required=False)
parser.add_argument('--mem_rss', dest='mem_rss', action='store_true', help='Plot used by this PID RAM (Gb) [= RSS - the portion of memory occupied by a process] vs time (s).', default=False, required=False)
parser.add_argument('--pmem', dest='pmem', action='store_true', help='Plot used by this PID RAM (percent) vs time (s).', default=False, required=False)
parser.add_argument('--pcpu', dest='pcpu', action='store_true', help='Plot used by this PID CPU (percent) vs time (s).', default=False, required=False)
parser.add_argument('--avail_space', dest='avail_space', action='store_true', help='Plot free disk space on partition with watched dir (Gb) vs time (s).', default=False, required=False)
parser.add_argument('--dir_size', dest='dir_size', action='store_true', help='Plot watched dir size (Gb) vs time (s).', default=False, required=False)
parser.add_argument('--plot_all', dest='plot_all', action='store_true', help='Switches on all plotting.', default=False, required=False)


def get_pcpu_pmem(pid):
    try:
        process = psutil.Process(pid)
        pmem = process.memory_percent() # % of memory used
        mem_rss = process.memory_info().rss # rss = residen set size is the portion of memory occupied by a process
        pcpu = process.cpu_percent(interval=0.02) # % of CPU used
        for child in process.children(recursive=True):
            try:
                pmem += child.memory_percent()
                pcpu += child.cpu_percent(interval=0.02)
                mem_rss += child.memory_info().rss
            except:
                pass
        mem = psutil.virtual_memory() # total memory available
        mem_rss = (mem_rss*1.0)/(1024*1024*1024)
        mem_avail = (mem.available*1.0)/(1024*1024*1024)
        exited = 0
    except:
        exited = 1
    return mem_avail, mem_rss, pmem, pcpu, exited

def get_avail_space(wdir):
    '''Monitors available disk space.'''
    command = "df "+wdir
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    avail_space = str(out.split(b'\n')[1]).split()[3] # e.g. Filesystem Size Used Avail Use% Mounted on'\n'/dev/xvdb1 1008G 721G 236G 76% /mnt/data1
    return (int(avail_space)*1.0)/(1024*1024) # disk space in Gb

def get_dir_size(wdir):
    '''Iterates over all files and subfolders in 'wdir' and returns total size of the folder in Gb.'''
    dir_size = 0
    for dirpath, dirnames, filenames in os.walk(wdir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                dir_size += os.path.getsize(fp)
            else:
                pass # e.g. Permission Denied
    return (dir_size*1.0)/(1024*1024*1024)

# read arguments
args = parser.parse_args()

if not args.plot: # then write logfile
    pid = args.pid # this is the only required argument
    if not psutil.pid_exists(pid):
        print ( "No process with PID" , pid , "found", file=sys.stderr)
        exit(1)

    if not args.out:
        out_file_name = str(pid)
    else:
        out_file_name = args.out

    #  generate outfile name
    t_start = time.time()
    out_file_name = out_file_name +".log"
    outfile = open(out_file_name,"w")

    outfile.write('\t'.join(["time","pid","avail_mem","mem_rss","%mem","%cpu","wdir_size","free_space"])+'\n')
    while True:
        if psutil.pid_exists(pid):
            mem_avail,mem_rss,pmem,pcpu,exited = get_pcpu_pmem(pid)
            if exited:
                print ( "Process with PID" , pid , "was terminated ...",file=sys.stderr)
                break
            dir_size = get_dir_size(args.wdir)
            space_avail = get_avail_space(args.wdir)
            outfile.write('%d\t%d\t%.1f\t%.1f\t%.2f\t%.2f\t%.1f\t%.1f\n' % (time.time()-t_start,pid,mem_avail,mem_rss,pmem,pcpu,dir_size,space_avail))
            outfile.flush()
        else:
            print ( "Process with PID" , pid , "was terminated ...",file=sys.stderr)
            break
        time.sleep(args.time_step)

    outfile.close()
    time.sleep(5)
else:
    out_file_name = args.plot #otherwise log file is provided by user

#read the resulting file to pandas
if args.plot_all or args.avail_pmem or args.mem_rss or args.pmem or args.pcpu or args.dir_size or args.avail_space:
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    df = pd.read_csv(out_file_name,sep='\t')
#plot with pylab
if args.avail_pmem or args.plot_all:  # avail_mem
    fig1 = df.plot(x='time', y=["avail_mem"],title="available memory, Gb",kind='line').get_figure()
    fig1.savefig(out_file_name.split('.')[0]+'.avail_mem.png')
if args.mem_rss or args.plot_all: # RSS
    fig2 = df.plot(x='time', y=["mem_rss"],title ="RSS, Gb",kind='line').get_figure()
    fig2.savefig(out_file_name.split('.')[0]+'.mem_rss.png')
if args.pmem or args.plot_all: #%mem
    fig3 = df.plot(x='time', y=["%mem"],title = "% of memory used",kind='line').get_figure()
    fig3.savefig(out_file_name.split('.')[0]+'.pmem.png')
if args.pcpu or args.plot_all: #%cpu
    fig4 = df.plot(x='time', y=["%cpu"],title = "% of CPU used",kind='line').get_figure()
    fig4.savefig(out_file_name.split('.')[0]+'.pcpu.png')
if args.dir_size or args.plot_all:
    fig5 = df.plot(x='time', y=["wdir_size"],title = "Directory "+str(args.wdir)+" size, Gb",kind='line').get_figure()
    fig5.savefig(out_file_name.split('.')[0]+'.dir_size.png')
if args.avail_space or args.plot_all:
    fig6 = df.plot(x='time', y=["free_space"],title = "Remaining disk space, Gb",kind='line').get_figure()
    fig6.savefig(out_file_name.split('.')[0]+'.avail_space.png')

# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# RhodeCode Enterprise Edition, including its added features, Support services,
# and proprietary license terms, please see https://rhodecode.com/licenses/

"""
This is a standalone script which will start VCS and RC.

Performance numbers will be written on each interval to:
    vcs_profileX.csv
    rc_profileX.csv

To stop the script by press Ctrl-C
"""

import datetime
import os
import psutil
import subprocess
import sys
import time
import traceback
import urllib

PROFILING_INTERVAL = 5
RC_WEBSITE = "http://localhost:5001/"


def get_file(prefix):
    out_file = None
    for i in xrange(100):
        file_path = "%s_profile%.3d.csv" % (prefix, i)
        if os.path.exists(file_path):
            continue
        out_file = open(file_path, "w")
        out_file.write("Time; CPU %; Memory (MB); Total FDs; Dulwich FDs; Threads\n")
        break
    return out_file


def dump_system():
    print "System Overview..."
    print "\nCPU Count: %d (%d real)" % \
          (psutil.cpu_count(), psutil.cpu_count(logical=False))
    print "\nDisk:"
    print psutil.disk_usage(os.sep)
    print "\nMemory:"
    print psutil.virtual_memory()
    print "\nMemory (swap):"
    print psutil.swap_memory()


def count_dulwich_fds(proc):
    p = subprocess.Popen(["lsof", "-p", proc.pid], stdout=subprocess.PIPE)
    out, err = p.communicate()

    count = 0
    for line in out.splitlines():
        content = line.split()
        # http://git-scm.com/book/en/Git-Internals-Packfiles
        if content[-1].endswith(".idx"):
            count += 1

    return count

def dump_process(pid, out_file):
    now = datetime.datetime.now()
    cpu = pid.cpu_percent()
    mem = pid.memory_info()
    fds = pid.num_fds()
    dulwich_fds = count_dulwich_fds(pid)
    threads = pid.num_threads()

    content = [now.strftime('%m/%d/%y %H:%M:%S'),
               cpu,
               "%.2f" % (mem[0]/1024.0/1024.0),
               fds, dulwich_fds, threads]
    out_file.write("; ".join([str(item) for item in content]))
    out_file.write("\n")


# Open output files
vcs_out = get_file("vcs")
if vcs_out is None:
    print "Unable to enumerate output file for VCS"
    sys.exit(1)
rc_out = get_file("rc")
if rc_out is None:
    print "Unable to enumerate output file for RC"
    sys.exit(1)

# Show system information
dump_system()

print "\nStarting VCS..."
vcs = psutil.Popen(["vcsserver"])
time.sleep(1)
if not vcs.is_running():
    print "VCS - Failed to start"
    sys.exit(1)
print "VCS - Ok"

print "\nStarting RhodeCode..."
rc = psutil.Popen("RC_VCSSERVER_TEST_DISABLE=1 paster serve test.ini",
                  shell=True, stdin=subprocess.PIPE)
time.sleep(1)
if not rc.is_running():
    print "RC - Failed to start"
    vcs.terminate()
    sys.exit(1)

# Send command to create the databases
rc.stdin.write("y\n")

# Verify that the website is up
time.sleep(4)
try:
    urllib.urlopen(RC_WEBSITE)
except IOError:
    print "RC - Website not started"
    vcs.terminate()
    sys.exit(1)
print "RC - Ok"

print "\nProfiling...\n%s\n" % ("-"*80)
while True:
    try:
        dump_process(vcs, vcs_out)
        dump_process(rc, rc_out)
        time.sleep(PROFILING_INTERVAL)
    except Exception:
        print traceback.format_exc()
        break

# Finalize the profiling
vcs_out.close()
rc_out.close()

vcs.terminate()
rc.terminate()

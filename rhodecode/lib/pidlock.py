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

import os
import errno

from multiprocessing.util import Finalize

from rhodecode.lib.compat import kill


class LockHeld(Exception):
    pass


class DaemonLock(object):
    """daemon locking
    USAGE:
    try:
        l = DaemonLock(file_='/path/tolockfile',desc='test lock')
        main()
        l.release()
    except LockHeld:
        sys.exit(1)
    """

    def __init__(self, file_=None, callbackfn=None,
                 desc='daemon lock', debug=False):

        lock_name = os.path.join(os.path.dirname(__file__), 'running.lock')
        self.pidfile = file_ if file_ else lock_name
        self.callbackfn = callbackfn
        self.desc = desc
        self.debug = debug
        self.held = False
        #run the lock automatically !
        self.lock()
        self._finalize = Finalize(self, DaemonLock._on_finalize,
                                  args=(self, debug), exitpriority=10)

    @staticmethod
    def _on_finalize(lock, debug):
        if lock.held:
            if debug:
                print 'leck held finilazing and running lock.release()'
            lock.release()

    def lock(self):
        """
        locking function, if lock is present it
        will raise LockHeld exception
        """
        lockname = '%s' % (os.getpid())
        if self.debug:
            print 'running lock'
        self.trylock()
        self.makelock(lockname, self.pidfile)
        return True

    def trylock(self):
        running_pid = False
        if self.debug:
            print 'checking for already running process'
        try:
            with open(self.pidfile, 'r') as f:
                try:
                    running_pid = int(f.readline())
                except ValueError:
                    running_pid = -1

            if self.debug:
                print ('lock file present running_pid: %s, '
                       'checking for execution' % (running_pid,))
            # Now we check the PID from lock file matches to the current
            # process PID
            if running_pid:
                try:
                    kill(running_pid, 0)
                except OSError as exc:
                    if exc.errno in (errno.ESRCH, errno.EPERM):
                        print ("Lock File is there but"
                               " the program is not running")
                        print "Removing lock file for the: %s" % running_pid
                        self.release()
                    else:
                        raise
                else:
                    print "You already have an instance of the program running"
                    print "It is running as process %s" % running_pid
                    raise LockHeld()

        except IOError as e:
            if e.errno != 2:
                raise

    def release(self):
        """releases the pid by removing the pidfile
        """
        if self.debug:
            print 'trying to release the pidlock'

        if self.callbackfn:
            #execute callback function on release
            if self.debug:
                print 'executing callback function %s' % self.callbackfn
            self.callbackfn()
        try:
            if self.debug:
                print 'removing pidfile %s' % self.pidfile
            os.remove(self.pidfile)
            self.held = False
        except OSError as e:
            if self.debug:
                print 'removing pidfile failed %s' % e
            pass

    def makelock(self, lockname, pidfile):
        """
        this function will make an actual lock

        :param lockname: acctual pid of file
        :param pidfile: the file to write the pid in
        """
        if self.debug:
            print 'creating a file %s and pid: %s' % (pidfile, lockname)

        dir_, file_ = os.path.split(pidfile)
        if not os.path.isdir(dir_):
            os.makedirs(dir_)
        with open(self.pidfile, 'wb') as f:
            f.write(lockname)
        self.held = True

# This software is provided under the MIT Open Source Software License:
#
# Copyright (c) 2016, Ariana Giroux (Eclectick Media Solutions)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time
import socket
import datetime as dt
import csv

from pythonping import ping as pyping


# GLOBALS
buildname = 'PingStats'
version = '2.1'
versiondate = 'Sun Dec  4 05:03:21 2016'
versionstr = 'PingStats Version %s (C) Ariana Giroux, Eclectick Media ' \
             'Solutions. circa %s' % (
                 version, versiondate)


class Core:
    @staticmethod
    def buildfile(path, name):
        if path is None:
            path = ''

        if name is not None and name.count('*'):
            raise ValueError('Illegal file name %s' % name)

        if name is None:
            name = buildname + 'Log.csv'
        else:

            name += '.csv'

        try:
            return open(path + name, 'a+')
        except OSError:
            print('Failed to open \'%s\', defaulting to \'%sLog.csv\'.' % (
                (path + name), buildname))
            return open('%sLog.csv' % buildname)

    @staticmethod
    def write_csv_data(writer, data):
        """ Writes a row of CSV data and returns the data that was read. """
        writer.writerow(data)
        return data

    @staticmethod
    def ping(address, timeout=3000, size=64, verbose=True):
        host_name = socket.gethostname()

        i = 1
        while 1:
            try:
                yield (dt.datetime.fromtimestamp(time.time()),
                       pyping.single_ping(address, host_name, timeout, i, size,
                       verbose=verbose)[0], timeout, size, address)
            except TypeError:
                yield (dt.datetime.fromtimestamp(time.time()),
                       -100.00, timeout, size, address)

            i += 1
            time.sleep(0.22)

    def __init__(self, address, file_path=None, file_name=None, nofile=False,
                 *args, **kwargs):
        # core.Core.ping
        if address is None:
            raise RuntimeError('core.Core requires address')
        self.address = address
        self.ping_generator = self.ping(self.address)

        # core.Core.build files
        self.file_path = file_path  # validated in self.build file
        self.file_name = file_name  # validated in self.build file
        self.nofile = nofile
        if not self.nofile:
            self.built_file = self.buildfile(self.file_path, self.file_name)
            self.cwriter = csv.writer(self.built_file)

    def __del__(self):
        self.built_file.close()

if __name__ == '__main__':
    raise DeprecationWarning('Direct execution of PingStats has been '
                             'deprecated, please use main.py')

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
import csv
import argparse
import datetime as dt
import atexit

import Plot
from pythonping import ping as pyping


# GLOBALS
buildname = 'PingStats'
version = '2.0.01'
versiondate = 'Sun Nov 13 06:39:04 2016'
versionstr = 'PingStats Version %s (C) Ariana Giroux, Eclectick Media ' \
             'Solutions. circa %s' % (
                 version, versiondate)


def buildfile(path, name):
    if path is None:
        path = ''

    if name is None:
        name = buildname + 'Log.csv'
    else:
        name += '.csv'

    return open(path + name, 'a+')


def write_csv_data(writer, data):
    """ Writes a row of CSV data.

    "file" - The file object to write to.
    "data" - The row to be saved.
    "terminal_output" - Boolean value to enable text output to the terminal.
    Returns the row written by the function.
    """
    writer.writerow(data)


def ping(address, timeout=3000, size=64, verbose=True):
    host_name = socket.gethostname()

    i = 1
    while 1:

        # TODO The current version of python-ping breaks PingStats.ping
        # The current implementation is several commits behind python-ping's
        # master. If the code is installed via the master, we need to add a
        # statement to handle the two return values (one of which we do not
        # need) by including a `[0]` to the end of the `pyping.single_ping`
        # call.
        yield (dt.datetime.fromtimestamp(time.time()),
               pyping.single_ping(address, host_name, timeout, i, size)[0],
               timeout, size, address)

        i += 1
        time.sleep(0.22)


# Bootstrap logic.

# TODO Parser logic should likely be handled explicitly on module load
if __name__ == '__main__':
    # Define program arguments.
    parser = argparse.ArgumentParser(
        description='%s. This program defines some basic ping statistic '
                    'visualizationmethods through Python\'s \'matplotlib\'.'
                    % versionstr)

    parser.add_argument('-a', '--address', help='The IP address to ping.')

    parser.add_argument('-p', '--path',
                        help='The path to output csv files to')

    parser.add_argument('-pf', '--plotfile',
                        help='Include the path to a previously generated CSV'
                             'file to generate a plot.')

    parser.add_argument('-gi', '--generateimage',
                        help='Used in conjunction with the -pf option, this '
                             'option sends a name for a \'*.png\' file to save'
                             ' to the current working directory.')

    parser.add_argument('-n', '--name',
                        help='Flag this option to use a custom name for the'
                             ' CSV output file.')

    parser.add_argument('-s', '--showliveplot',
                        help='Flag this option to display an animated plot of'
                             'the last 500 ping sequences.',
                        action='store_true')

    parser.add_argument('-sF', '--refreshfrequency',
                        help='Specify a number of milliseconds to wait between'
                             'refreshes of the -s plot visualization feature.'
                             'The lower the number, the better the performance'
                             'of %s visualization. Handy for \"potatoes\"'
                             % buildname)

    parser.add_argument('-sL', '--tablelength',
                        help='The total number of pings to show for -s. The'
                             'lower the number, the better the performance of '
                             '%s visualization. Handy for \"potatoes.\"'
                             % buildname)

    parser.add_argument('-sNF', '--nofile',
                        help='Flag this option to disable outputting ping '
                             'information to a csv  file during live plotting.'
                             ' Helps with memory consumption.',
                        action='store_true')

    parser.add_argument('-v', '--version',
                        help='Flag this option to display software version.',
                        action='store_true')

    parsed = parser.parse_args()

    if parsed.version:
        print(versionstr)
    elif parsed.address is not None:
        if parsed.showliveplot:
            print(  # TODO Update output on program start.
                'Pinging %s...\nThe longer that this program runs, the more '
                'system resources it will occupy. Please consider using the '
                'live plotting feature for shorter run times (i.e a match of '
                'on line chess).\n Close the plot window to exit the'
                ' program....' % parsed.address)

            cwriter = None
            if not parsed.nofile:
                cwriter = csv.writer(buildfile(parsed.path, parsed.name))

            # TODO When showing a live plot, no information is logged via csv

            p = ping(parsed.address)

            plot = Plot.Animate(p, parsed.tablelength, parsed.refreshfrequency)
            plot.animate()

            atexit.register(plot.close_thread)  # TODO Fix exit logic.
            # Matplotlib and the `plot.get_pings` objects don't play nicely
            # with  user exit.

        else:
            print(
                'Pinging %s...\nThe longer that this program runs, the larger '
                'the resulting CSV file will be.\nDue to  the way that the '
                'program handles the output file, do not open the .csv file '
                'created by this application until you are finished gathering '
                'pings.\nPress CTR+C to exit...' % parsed.address)

            if not parsed.nofile:
                cwriter = csv.writer(buildfile(parsed.path, parsed.name))

            for return_tuple in ping(parsed.address):
                if not parsed.nofile:
                    write_csv_data(cwriter, return_tuple)

    elif parsed.plotfile is not None:
        Plot.PlotFile(parsed.plotfile)
    else:
        parser.print_usage()

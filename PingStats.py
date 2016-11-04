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
import datetime as dt
import socket
import csv
import argparse
# from threading import Thread  # Used for live plot generation

import Plot
from pythonping import ping as pyping

""" Preamble

This software attempts to bring a simple python utility for logging ping
results to CSV files, and representing them graphically via Python's
Matplotlib. The software aims to achieve this in as minimal, "readable," and
resource effective a way as possible.

This software analyzes data recorded into CSV files by itself to either present
an interactive plot (provided by the Matplotlib package) or generate an image
of a plot for specific logs.

This software also has the capability to display ping information as it is
received, mapping it by time read and return time of each packet read. When
presenting information as it is received, the software does not write data to a
CSV log, instead relying on the use of the live presentation to present its
information. It can however be instructed to output information to a log for
further usage for very minimal system resource cost. """

""" Technical Notes

It should be noted that the software inherently uses more system resources
while displaying graphics to the screen, as this software is intended to be
run on as minimal a software as possible.

Due to the variance on OS dependent ping packages, data collection may not
work, and may need tweaking. The .dataparser() function is intended to be
rewritten if possible. Due to this need to be easy to rewrite, the language is
as simplified as it can be, using only for loop structures and a few if
statements. If you find the initially provided code to be hard to interpret,
uncomment the `# DEBUG:' lines to have python slowly iterate through each
sequence of data and show the results provided."""

# GPS discussion

# Record GPS coordinates from www.ipinfo.io requests whilst on non-mobile OS's.
# Plot a "heat map" of GPS coordinates and how fast/slow their connection was.

""" GPS Functionality Preamble
This software could be effectively used for mapping connection rate in various
locations. This could allow the user to map connection speeds throughout their
city/region. This would be useful for people who move from location to location
on a regular basis, and require fast Internet connections everywhere they go.

Due to the variance in where this software could be used over time, it should
be able to collect data from several PingStatsLog.csv files and present them to
the user overlaid on a map where the faster connections are presented as a red
"heat zones." """

""" GPS Functionality Technical notes
This software could use a kivy (see www.kivy.org) application to gather GPS
coordinates. This would require a major overhaul of the application structure,
and should likely be handled in a fork.

The Kivy framework provides GPS functionality with Plyer
(https://github.com/kivy/plyer), and provides a convienient and well
established framework for Multi-platform application development. Using this
framework, the software could easily provide a graphical presentation on the
various options available to this software already."""

# GLOBALS
buildname = 'PingStats'
version = '1.0.04.2'
versiondate = 'Thu Aug  4 00:34:10 2016'
versionstr = 'PingStats Version %s (C) Ariana Giroux, Eclectick Media ' \
             'Solutions. circa %s' % (
                 version, versiondate)

NT_ICMQSEQNUM = 0  # Used to ensure ICMQ sequence number consistency on NT
# based systems.


def buildfile(path, name):
    if path is None:
        path = ''

    if name is None:
        name = buildname + 'Log.csv'
    else:
        name += '.csv'

    return open(path + name, 'a+')


# TODO Initialize a CSV.writer object before execution of write_csv_data().
""" Currently, write_csv_data() initializes a new CSV.writer object every time
it is called. This results in the program working extra iterations on automatic
garbage collection for the item.

The CSV.writer object only needs to be initialized once to maintain the
functionality that we are looking for. The only struggle will be getting the
object into the runtime safely, without running into issues with threading
buffer overruns. """


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

        yield (time.time(),
               pyping.single_ping(address, host_name, timeout, i, size),
               timeout, size, address)
        i += 1


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
            print(
                'Pinging %s...\nThe longer that this program runs, the more '
                'system resources it will occupy. Please consider using the '
                'live plotting feature for shorter run times (i.e a match of '
                'on line chess).\n Close the plot window to exit the'
                ' program....' % parsed.address)

            if not parsed.nofile:
                cwriter = csv.writer(buildfile(parsed.path, parsed.name))

            p = ping(parsed.address)
            plot = Plot.Animate()

            plot.animate()

            for return_tuple in p:
                if not parsed.nofile:
                        write_csv_data(cwriter, return_tuple)
                plot.ptable.appendx(dt.datetime.fromtimestamp(float(
                    return_tuple[0])))
                if return_tuple[1] is not None:
                    plot.ptable.appendy(return_tuple[1])
                else:
                    plot.ptable.appendy(-10)

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

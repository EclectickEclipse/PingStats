
# This software is provided under the MIT Open Source Software License:
#
# Copyright (c) 2016, Ariana Giroux (Eclectick Media Solutions)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import shlex
import subprocess
import time
import csv
import os
import argparse
import sys
havematplot = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib import style
    havematplot = True
except OSError as e:
    sys.stderr.write('Could not load matplotlib!\n')

# TODO Build an interactive mode.
# TODO Further document preamble.

buildname = 'PingStats'
version = '0.08'
versiondate = 'Wed Apr 27 01:38:01 2016'
versionstr = 'PingStats Version %s (C) Ariana Giroux, Eclectick Media Solutions, circa %s' % (version, versiondate)


def buildfiles(path, name):
    """ Builds the files used for processing.

    :param path: The path to output the files to.
    :param name: The custom name supplied by the user.
    :return: A tuple containing the csvfile object and the outfile object.
    """
    try:
        if name is not None:  # If user specified a custom name.
            if path is not None:  # If user specified an output path.
                csvfile = open('%s%s-%s.csv' % (path, name, time.ctime()), 'w+')
                outfile = open('%sout.txt' % path, 'w+')
                return csvfile, outfile
            else:
                csvfile = open('%s-%s.csv' % (name, time.ctime()), 'w+')
                outfile = open('out.txt', 'w+')
                return csvfile, outfile
        else:

            if path is not None:  # If user specified an output path.
                csvfile = open('%s%slog-%s.csv' % (path, buildname, time.ctime()), 'w+')
                outfile = open('%sout.txt' % path, 'w+')
                return csvfile, outfile
            else:
                csvfile = open('%sLog-%s.csv' % (buildname, time.ctime()), 'w+')
                outfile = open('out.txt', 'w+')
                return csvfile, outfile
    except OSError as e:
        print('Please ensure you have included a legal path!\n%s, %s' % (e.errno, e.strerror))
        quit()  # break


def writecsv(file, row):
    """ Writes a row of CSV data.

    :param file: The file object to write to.
    :param row: The row to be saved.
    :return: The row written by the process.
    """
    # TODO Should writecsv() be handled by dataparser?
    cwriter = csv.writer(file)
    cwriter.writerow(row)
    print('Wrote row: %s' % row)


def dataparser(datafile):
    """Parses through lines of text returned by ping and further refines it. This function creates a generator that can
    be iterated through in a for loop. For example:

    '''

    t = []

    for data in dataparser(dfile, cfile):
        table.append(data)
    '''

    :param datafile: The position of the log file to read.
    :return: The lines read.
    """

    data = datafile.readline()
    if len(data) is 0:
        return None  # hang until new line is written.

    row = [str(time.time())]

    if os.name != 'nt':
        # Parse data text
        if data.lower().count('cannot resolve') > 0 or data.lower().count('request timeout'):
            row.append('failed')  # Error line.
            row.append('failed')
            row.append('icmp_seq=%s' % data.split()[-1])
            row.append('ttl=0')
            row.append('time=-10')
            sys.stderr.write(data)
            # row.append(data)

        elif (data.count('PING') > 0 or data.lower().count('statistics') > 0 or  # break on ping end.
              data.lower().count('transmitted') > 0 or data.lower().count('round-trip') > 0):
            return None  # Exclude line.

        else:
            for val in data.split():  # Split lines by space and iterate.

                if val.count('bytes') > 0 or val.count('from') > 0 or val.count('ms') > 0 or \
                             val.count('\x00') > 0:  # skippable values
                    pass

                elif len(row) is 1:  # if this is the first data field.
                    row.append('size=%s' % val)

                elif len(row) is 2:  # if this is the second data field.
                    row.append(val[:-1])

                else:  # append data.
                    row.append(val)
    else:  # TODO Define parsing logic for lines on NT based ping requests.
        raise (KeyboardInterrupt, 'Software not supported on NT based systems as of V0.08')

    if len(row) > 1:  # if data was found, yield row.
        return row
    else:
        print(row)
        return None


# TODO Remove pingfrequency argument, current build does not use it.
def ping(address, customarg=None, wait=None,pingfrequency=None, outfile=None):
    """ Runs a ping and collects statistics.
    :param address: The address to ping.
    :param customarg: A string with user specified custom arguments.
    :param wait: An integer value specifying how long to wait.
    :param pingfrequency: The amount of time between spawning new ping processi.
    :param outfile: The file object to write output to.
    """
    # Conversion handlers.
    # TODO Should ping() handle arguments inside functions or inside initial runtime as current?

    # Address handler.
    if address is None:  # ensure a host was specified.
        sys.stderr.write('Please include at least one option...\nType -h for help...\n')
        quit()  # Break

    # Wait handler.
    if type(wait) is str:
        try:
            wait = int(wait)
        except ValueError:
            sys.stderr.write('Please enter numbers only for the -t flag.\n')
            quit()

    # handle pingfrequency argument logic.
    if pingfrequency is None:
        pingfrequency = 60
    elif type(pingfrequency) is str:
        try:
            pingfrequency = int(pingfrequency)
        except ValueError:  # Handle non integer values....
            sys.stderr.write('Please specify a number with the -f option.\n')
            exit()  # break

    def parsearg(custom_argument):
        """ Creates an argument for the subprocess.Popen object.

        :param custom_argument: The custom argument specified by the user (or None for no custom argument)
        :return: A mutable list containing the argument to use in the subprocess.Popen object.
        """
        if custom_argument is not None:
            return ['ping', shlex.split(custom_argument), address]
        else:
            if os.name == 'nt':
                return ['ping', '-t', address]
            else:
                return ['ping', address]

    def ping(argument, file):
        """ Pings a host.

        :param argument: A mutable list to use for the subprocess.Popen object.
        :param file: An output file.
        :return: The process object.
        """
        return subprocess.Popen(argument, stdout=file)

    process = ping(parsearg(customarg), outfile)

    return process, outfile.name


# TODO Define a backend for matplotlib that enables bundled usage.
def showliveplot(datafile, csvfile, refreshfreq, tablelength):
    """ Shows a live graph of the last 500 rows of the specified CSV file on an interval of 60 seconds.

    :param datafile: The path of the file to be read.
    :return: The matplotlib.animation.FunAnimation object.
    """

    class PlotTable:

        def __init__(self, tablelength):
            self.x = []
            self.y = []
            if tablelength is None:
                self.tablelength = 200
            else:
                self.tablelength = int(tablelength)

        def appendx(self, a):
            if len(self.x) < self.tablelength:
                self.x.append(a)
            else:
                self.x.pop(0)
                self.x.append(a)

        def appendy(self, a):
            if len(self.y) < self.tablelength:
                self.y.append(a)
            else:
                self.y.pop(0)
                self.y.append(a)

        def getx(self):
            return self.x

        def gety(self):
            return self.y

    # TODO BUG ShowplotDeployment: Currently, using the MacOSx matplotlib backend, this function will not compile.
    # TODO BUG ShowplotDeployment: Does not render without using the MacOSx backend without further dependencies.
    style.use('fivethirtyeight')

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    table = PlotTable(tablelength)

    def animate(i):
        """ Reads rows from a CSV file and render them to a plot.

        :param i: Arbitrary.
        :return: None
        """
        d = dataparser(datafile)
        # print(d)
        if d is not None:  # implies new information was gotten.
            writecsv(csvfile, d)
            table.appendx(d[3].split('=')[1])
            table.appendy(d[5].split('=')[1])
        ax1.clear()
        ax1.plot(table.getx(), table.gety())

    plt.xlabel('ICMP SEQ #.')
    plt.ylabel('Return time.')
    # DEBUG
    # sys.stderr.write('Showing plot...\n')
    if refreshfreq is None:
        ani = animation.FuncAnimation(fig, animate, interval=500)
    else:
        ani = animation.FuncAnimation(fig, animate, interval=int(refreshfreq))

    plt.show()
    return ani


def showplot_fromfile(csvfilepath):
    style.use('fivethirtyeight')

    fig = plt.figure()

    table = []

    with open(csvfilepath) as cf:
        creader = csv.reader(cf)
        for line in creader:
            table.append(line)

    x = []
    y = []

    for row in table:
        x.append(row[3].split('=')[1])
        y.append(row[5].split('=')[1])

    plt.plot(x, y)

    plt.ylabel('Return Time')
    plt.xlabel('ICMP SEQ')
    plt.show()  # hangs until user closes plot.

# Bootstrap logic.

if __name__ == '__main__':
    # Define program arguments.
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--address', help='The IP address to ping.')

    parser.add_argument('-c', '--customarg', help='Define your own argument for the ping.'
                                                  'If you are experiencing issues with pings ending before intended,'
                                                  'try using \'-c \"-c 999999999\"\' to spawn a process with an '
                                                  'extremely long runtime.')

    # TODO Rename --destination to --path for clarity.
    parser.add_argument('-d', '--destination', help='To supply a specific path to output any files to, include a path.')

    parser.add_argument('-F', '--pingfrequency', help='The frequency with which to ping the host. Defaults to 0.25 '
                                                      'seconds.')

    parser.add_argument('-pf', '--plotfile', help='Include the path to a previously generated CSV file to generate a '
                                                  'plot.')

    parser.add_argument('-n', '--name', help='Flag this option to use a custom name for the CSV output file.')

    parser.add_argument('-s', '--showliveplot', help='Flag this option to display an animated plot of the last 500 ping'
                                                     ' sequences.', action='store_true')

    parser.add_argument('-sF', '--refreshfrequency', help='Specify a number of milliseconds to wait between refreshes'
                                                          'of the -s plot visualization feature. THe lower the number,'
                                                          'the better the performance of %s visualization. Handy for'
                                                          '\"potatoes\"' % buildname)

    parser.add_argument('-sL', '--tablelength', help='The total number of pings to show for -s. The lower the number, '
                                                     'the better the performance of %s visulization. Handy for '
                                                     '\"potatoes.\"' % buildname)

    parser.add_argument('-t', '--time', help='The time to wait before killing the process in seconds.')

    parser.add_argument('-v', '--version', help='Flag this option to display software version.', action='store_true')

    parsed = parser.parse_args()

    if parsed.version:
        print(versionstr)
    elif parsed.address is not None:
        if parsed.showplot:  # TODO build animation logic.
            print('Pinging %s...\nThe longer that this program runs, the larger the resulting CSV file will be.\n'
                  'Press CNTRL+C to exit...' % parsed.address)

            csvfile, outfile = buildfiles(parsed.destination, parsed.name)

            # TODO Deprecate calls to --pingfrequency
            p, l = ping(parsed.address, customarg=parsed.customarg, pingfrequency=parsed.pingfrequency,
                        outfile=outfile)

            with open(outfile.name) as df:
                showliveplot(df, csvfile, parsed.refreshfrequency, parsed.tablelength)
                # hangs while showing a plot, when user closes plot, process closes.

            p.kill()
            csvfile.close()
            outfile.close()
            os.remove(outfile.name)


        else:
            print('Pinging %s...\nThe longer that this program runs, the larger the resulting CSV file will be.\n'
                  'Press CNTRL+C to exit...' % parsed.address)

            csvfile, outfile = buildfiles(parsed.destination, parsed.name)

            # TODO Deprecate calls to --pingfrequency
            p, l = ping(parsed.address, customarg=parsed.customarg, pingfrequency=parsed.pingfrequency,
                        outfile=outfile)

            try:
                with open(outfile.name) as df:
                    while p.poll() is None:
                        d = dataparser(df)
                        if d is not None:
                            writecsv(csvfile, d)

            except (KeyboardInterrupt, SystemExit):
                p.kill()
                csvfile.close()
                outfile.close()
                os.remove(outfile.name)
    elif parsed.plotfile is not None:
        showplot_fromfile(parsed.plotfile)

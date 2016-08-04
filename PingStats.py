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
import datetime as dt
import time
import csv
import os
import argparse
import sys
import tempfile

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib import style
except OSError as e:
    raise RuntimeError('Could not load matplotlib!')

""" Preamble

This software attempts to bring a simple python utility for logging ping results to CSV files, and representing them
graphically via Python's Matplotlib. The software aims to achieve this in as minimal, "readable," and resource
effectively as possible.

This software analyzes data recorded into CSV files by itself to either present an interactive plot (provided by the
Matplotlib package) or generate an image of a plot for specific logs.

This software also has the capability to display ping information as it is recieved, mapping it by time read and return
time of each packet read. When presenting information as it is recieved, the software does not write data to a CSV log,
instead relying on the use of the live presentation to present its information. It can however be instructed to output
information to a log for further usage for very minimal system resorce cost. """

""" Technical Notes

It should be noted that the software inherently uses more system resources while displaying graphics to the screen, as
this software is intended to be run on as minimal a software as possible.

Due to the variance on OS dependent ping packages, data collection may not work, and may need tweaking. The
.dataparser() function is intended to be rewritten if possible. Due to this need to be easy to rewrite, the language is
as simplified as it can be, using only for loop structures and a few if statements. If you find the initially provided
to be hard to interpret, uncomment the `# DEBUG:' lines to have python slowly iterate through each sequence of data
and show the results provided."""

# TODO Create `# DEBUG:' lines in .dataparser()


# TODO Build an interactive mode.
# TODO Record GPS coordinates from www.ipinfo.io requests whilst on non-mobile OS's.
# TODO Plot a "heat map" of GPS coordinates and how fast/slow their connection was.

""" GPS Functionality Preamble
This software could be effectively used for mapping connection rate in various locations. This could allow the user
to map connection speeds throughout their city/region. This would be useful for people who move from location to
location on a regular basis, and require fast internet connections everywhere they go.

Due to the variance in where this software could be used over time, it should be able to collect data from several
pingstatslog files and present them to the user overlaid on a map where the faster connections are presented as a red
"heat zones." """

""" GPS Functionality Technical notes
This software could use a kivy (see www.kivy.org) application to gather GPS coordinates. This would require a major
overhaul of the application structure, and should likely be handled in a fork.

The Kivy framework provides GPS functionality with Plyer (https://github.com/kivy/plyer), and provides a convienient
and well established framework for Multiplatform application developement. Using this framework, the software could
easily provide a graphical presentation on the vairous options available to this software already."""

# GLOBALS
buildname = 'PingStats'
version = '1.0.04.1'
versiondate = 'Wed Jul 27 23:52:58 2016'
versionstr = 'PingStats Version %s (C) Ariana Giroux, Eclectick Media Solutions, circa %s' % (version, versiondate)

NT_ICMQSEQNUM = 0  # Used to ensure icmq sequence number consistency on NT based systems.


def buildfiles(path, name):
    """ Builds the files used for processing. For unix machines, generates a temporary file for ping output. Due to
    Temporary File limitations on Windows NT softwares, This function will generate a new folder in the install location
    of PingStats on the host OS.

    :param path: The path to output the CSV file to.
    :param name: The custom name supplied by the user.
    :return: A tuple containing the csvfile object and the outfile object.
    """

    # First, convert args.

    if path is None:
        path = ''
    elif name is None:
        name = ''

    # Apply user arguments.

    try:
        dest = path + name + '.csv'
    except TypeError:
        sys.stderr.write('Could not parse specified arguments, defaulting to ./Log.csv\n')
        dest = buildname + 'Log.csv'

    try:
        csvfile = open(dest, 'a+')  # actually open the CSV file at destination path.
    except OSError:
        raise RuntimeError('Please ensure that you use the full legal path to output the CSV file to.')

    if os.name == 'nt':  # Handle windows file creation.

        if os.getenv('LOCALAPPDATA', False):  # Check for localappdata environment variable.

            if os.access(os.getenv('LOCALAPPDATA'), os.F_OK):  # check for access to localappdata location.

                if not os.access(os.path.join(os.getenv('LOCALAPPDATA'), 'PingStats'), os.F_OK):  # If no folder exists
                    os.mkdir(os.path.join(os.getenv('LOCALAPPDATA'), 'PingStats'))  # Make new folder,
                    dfile = open(os.path.join(os.getenv('LOCALAPPDATA'), 'PingStats\\DataOutput.txt'), 'a+')  # build

                else:  # Implies that the pingstats folder exists.
                    dfile = open(os.path.join(os.getenv('LOCALAPPDATA'), 'PingStats\\DataOutput.txt'), 'a+')

            else:
                raise RuntimeError('FATAL ERROR! PINGSTATS COULD NOT ACCESS %LOCALAPPDATA%!!!')

        else:
            raise RuntimeError('FATAL ERROR! PINGSTATS COULD NOT ACCESS %LOCALAPPDATA%!!! \nExiting....\n')

    else:  # Handle *Nix file creation.
        dfile = tempfile.NamedTemporaryFile('w+')

    return csvfile, dfile  # return built files.


# TODO Initialize a CSV.writer object before execution of writecsv().
# This is causing a small amount of data leakage, as more csvwriter objects get created than get deleated.
""" Currently, writecsv initializes a new CSV.writer object every time it is called. This results in the program
working extra iterations on automatic garbage collection for the item.

The CSV.writer object only needs to be initialized once to maintain the functionality that we are looking for. The only
struggle will be getting the object into the runtime safely, without running into issues with threading buffer
overuns. """


def writecsv(file, data, terminaloutput):
    """ Writes a row of CSV data.

    :param file: The file object to write to.
    :param data: The row to be saved.
    :param terminaloutput: Bool value to enable text output to the terminal.
    :return: The row written by the process.
    """
    cwriter = csv.writer(file)
    cwriter.writerow(data)
    rowtext = ''
    for val in data:
        rowtext += val + ', '
    if terminaloutput:
        print('Wrote row: \'%s\' to %s' % (rowtext, file.name))


def dataparser(datafile):
    """ Reads each line of data file for valid ping information, and once (or if) no new information is read, the
     function truncates the datafile and returns either a list of valid CSV rows, or None.

    :param datafile: The file to read for ping information.
    :return: A list of valid CSV rows for parsing by csvWriter() or None when no new valid information is found.
    """

    datalist = []  # a list of rows read in by dataparser.
    global NT_ICMQSEQNUM  # obtain icmq sequence counter.

    with open(datafile.name) as df:  # open the data file for reading

        for d in df:  # read datafile line by line, and parse lines for CSV output.
            # This is very logic heavy, and is not necessary to read through.
            datarow = [str(time.time())]

            # Parse data text
            if os.name != 'nt':
                if d.lower().count('cannot resolve') > 0 or d.lower().count('request timeout'):
                    datarow.append('failed')  # Error line.
                    datarow.append('failed')
                    datarow.append('icmp_seq=%s' % d.split()[-1])
                    datarow.append('ttl=0')
                    datarow.append('time=-10')
                    # sys.stderr.write(str(datarow))
                    # row.append(data)

                elif (d.count('PING') > 0 or d.lower().count('statistics') > 0 or  # break on ping end.
                      d.lower().count('transmitted') > 0 or d.lower().count('round-trip') > 0):
                    pass

                else:
                    for val in d.split():  # Split lines by space and iterate.

                        if val.count('bytes') > 0 or val.count('from') > 0 or val.count('ms') > 0 or \
                                        val.count('\x00') > 0:  # skippable values
                            pass

                        elif len(datarow) is 1:  # if this is the first data field.
                            datarow.append('size=%s' % val)

                        elif len(datarow) is 2:  # if this is the second data field.
                            datarow.append(val[:-1])

                        else:  # append data.
                            datarow.append(val)

            else:

                if d.lower().count('Request timed out.') > 1:
                    datarow.append('failed')
                    datarow.append('failed')
                    datarow.append('icmp_seq=%s' % NT_ICMQSEQNUM)
                    NT_ICMQSEQNUM += 1
                    datarow.append('ttl=0')
                    datarow.append('time-10')
                    # sys.stderr.write(datarow)

                elif d.lower().count('pinging') or d.lower().count('statistics') or d.lower().count('packets') or \
                        d.lower().count('approximate') or d.lower().count('minimum') or d.lower().count('control') or \
                        d.lower().count('^c') > 0:
                    pass

                else:
                    for val in d.split():

                        if val.lower().count('reply') or val.lower().count('from') > 0:
                            pass

                        elif val.lower().count('bytes') > 0:
                            datarow.insert(0, 'size=%s' % val.split('=')[1])

                        elif val.lower().count('time') > 0:
                            datarow.append(val)

                        elif val.lower().count('ttl') > 0:
                            datarow.insert(-2, val)

                        else:
                            datarow.append(val)

                    datarow.insert(2, 'icmp_seq=%s' % NT_ICMQSEQNUM)
                    NT_ICMQSEQNUM += 1

            # end parse

            # Check for row validity and append it to the list of read rows.
            if len(datarow) > 1:
                datalist.append(datarow)
            else:
                pass

    # data validity and size checks.
    if len(datalist) > 0:  # if data was found, return data and reduce filesize.
        datafile.seek(0)
        datafile.truncate()

        # DEBUG
        # with open(datafile.name) as f:
        #     print(f.read())

        return datalist

    else:  # no data read, reduce filesize, return None.
        datafile.seek(0)
        datafile.truncate()

        return []


def ping(address, customarg=None, ofile=None):
    """ Runs a ping and collects statistics.
    :param address: The address to ping.
    :param customarg: A string with user specified custom arguments.
    :param ofile: The file object to write output to.
    """
    # Conversion handlers.

    # Address handler.
    if address is None:  # ensure a host was specified.
        sys.stderr.write('Please include at least one option...\nType -h for help...\n')
        quit()  # Break

    # Argument handler.
    def parsearg(custom_argument):  # TODO Deprecate calls to this function, is inneficient.
        """ Creates an argument for the subprocess.Popen object.

        :param custom_argument: The custom argument specified by the user (or None for no custom argument)
        :return: A mutable list containing the argument to use in the subprocess.Popen object.
        This function is obtuse, and can be handled more efficiently,
        """
        if custom_argument is not None:
            return ['ping', shlex.split(custom_argument), address]
        else:
            if os.name == 'nt':
                return ['ping', '-t', address]
            else:
                return ['ping', address]

    return subprocess.Popen(parsearg(customarg), stdout=ofile)


# TODO Refactor .showliveplot() to a class.
""" .showliveplot() is looking more and more like a class. I feel like it is just prudent to refactor this to a
class."""


def showliveplot(datafile, cfile, refreshfreq, tablelength, nofile, terminaloutput):
    """ Shows a live graph of the last 50 rows of the specified CSV file on an interval of every half second.

    :param datafile: The file object used for data output.
    :param cfile: The file object used for CSV output
    :param refreshfreq: The frequency with which the matplotlib.animation.FuncAnimation object refreshes.
    :param tablelength: The number of objects to maintain on screen.
    :param nofile: The option to not output to a file.
    :return: The matplotlib.animation.FunAnimation object.
    """

    class PlotTable:
        """ A class to maintain a specified number of objects to plot to matplotlib. """

        def __init__(self, length):
            self.x = []
            self.y = []

            if length is None:
                self.length = 50
            else:
                self.length = int(tablelength)

        def appendx(self, a):
            """ Append a new value to the x value of the table. Maintains specified length of table upon reaching max.

            :param a: The value to append to the table.
            """
            if len(self.x) < self.length:
                self.x.append(a)
            else:
                self.x.pop(0)
                self.x.append(a)

        def appendy(self, a):
            """ Append a new value to the y value of the table. Maintains specified length of table upon reaching max.

            :param a: The value to append to the table.
            """
            if len(self.y) < self.length:
                self.y.append(a)
            else:
                self.y.pop(0)
                self.y.append(a)

        def getx(self):  # arbitrary get method
            return self.x

        def gety(self):  # arbitrary get method
            return self.y

    style.use('fivethirtyeight')

    fig = plt.figure()

    # build arg string for window titleing
    titlestring = ''
    for arg in sys.argv:
        if sys.argv.index(arg) is 0:
            pass
        else:
            titlestring += ' ' + arg
    fig.canvas.set_window_title('%s |%s' % (buildname + ' ' + version, titlestring))

    ax1 = fig.add_subplot(1, 1, 1)

    ptable = PlotTable(tablelength)

    def animate(i):
        """ Reads rows from a CSV file and render them to a plot.

        :param i: Arbitrary.
        :return: None
        """

        data_generator = dataparser(datafile)
        if data_generator is not None:
            for newrow in data_generator:  # some code linters may read this as NoneType, this is handled...
                if not nofile:
                    writecsv(cfile, newrow, terminaloutput)
                elif terminaloutput:
                    print(newrow)
                ptable.appendx(dt.datetime.fromtimestamp(float(newrow[0])))
                ptable.appendy(newrow[5].split('=')[1])

        ax1.clear()
        ax1.plot_date(ptable.getx(), ptable.gety(), '-', label='Connection over time')
        ax1.plot(ptable.getx(), ptable.gety())
        for label in ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        plt.xlabel('Timestamp')
        plt.ylabel('Return Time (in milleseconds)')
        plt.title('Ping Over Time')

    plt.subplots_adjust(left=0.13, bottom=0.33, right=0.95, top=0.89)
    print('Showing plot...\n')

    if refreshfreq is None:
        ani = animation.FuncAnimation(fig, animate, interval=500)
    else:
        ani = animation.FuncAnimation(fig, animate, interval=int(refreshfreq))

    ani.new_frame_seq()
    plt.show()

    return True


def showplot_fromfile(csvfilepath, imagename):
    """ Generates a plot from a csv file specified by the user. Also generates images of the file by supplying an
    imagename paramater.

    :param csvfilepath: The path to the file to generate.
    :param imagename: Optional argument to specify an image to generate.
    """
    style.use('fivethirtyeight')

    fig = plt.figure()

    # build arg string for window titleing
    titlestring = ''
    for arg in sys.argv:
        if sys.argv.index(arg) is 0:
            pass
        else:
            titlestring += ' ' + arg
    fig.canvas.set_window_title('%s |%s' % (buildname + ' ' + version, titlestring))

    ax1 = fig.add_subplot(1, 1, 1)

    table = []

    print('Reading ping information from user specified file.')
    with open(csvfilepath) as cf:
        creader = csv.reader(cf)
        for line in creader:
            table.append(line)

    x = []
    y = []

    for newrow in table:
        x.append(dt.datetime.fromtimestamp(float(newrow[0])))
        y.append(newrow[5].split('=')[1])

    ax1.plot(x, y)

    plt.subplots_adjust(left=0.13, bottom=0.33, right=0.95, top=0.89)

    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)

    plt.xlabel('Timestamp')
    plt.ylabel('Return Time (in milleseconds)')
    plt.title('Ping Over Time')

    if imagename is not None:  # User flagged -gi, generate an image.
        print('Generating %s.png.' % imagename)
        plt.savefig('%s.png' % imagename)
    else:  # Display plot.
        print('Showing the plot generated from \"%s.\"' % csvfilepath)
        plt.show()  # hangs until user closes plot.


# Bootstrap logic.

# TODO Parser logic should likely be handled explicitly on module load, instead of on bootstrap routine.
if __name__ == '__main__':
    # Define program arguments.
    parser = argparse.ArgumentParser(description='%s. This program defines some basic ping statistic visualization'
                                                 'methods through Python\'s \'matplotlib\'.' % versionstr)

    parser.add_argument('-a', '--address', help='The IP address to ping.')

    parser.add_argument('-g', '--gurusettings', help='For use by gurus: implement a custom argument to pass to the ping'
                                                     ' process.')

    parser.add_argument('-o', '--terminaloutput', help='Flag this option to output ping data to the terminal when they'
                                                       ' are read from the file.', action='store_true')

    parser.add_argument('-p', '--path', help='To supply a specific path to output any files to, include a path.')

    parser.add_argument('-pf', '--plotfile', help='Include the path to a previously generated CSV file to generate a '
                                                  'plot.')

    parser.add_argument('-gi', '--generateimage', help='Used in conjunction with the -pf option, this option sends a '
                                                       'name for a \'*.png\' file to save to the current working '
                                                       'directory.')

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

    parser.add_argument('-sNF', '--nofile', help='Flag this option to disable outputting ping information to a csv'
                                                 ' file during live plotting. Helps with memory consumption.',
                        action='store_true')

    parser.add_argument('-v', '--version', help='Flag this option to display software version.', action='store_true')

    parsed = parser.parse_args()

    if parsed.version:
        print(versionstr)
    elif parsed.address is not None:
        if parsed.showliveplot:
            print('Pinging %s...\nThe longer that this program runs, the more system resources it will occupy. Please'
                  'consider using the live plotting feature for shorter run times (i.e a match of online chess).\n'
                  'Close the plot window to exit the program....' % parsed.address)

            csvfile, outfile = buildfiles(parsed.path, parsed.name)

            p = ping(parsed.address, customarg=parsed.gurusettings, ofile=outfile)

            # hangs while showing a plot, when user closes plot, process closes.ile.name)
            showliveplot(outfile, csvfile, parsed.refreshfrequency, parsed.tablelength, parsed.nofile,
                         parsed.terminaloutput)

            # _ = str(input('Press enter to quit.'))  # Still does not force plot to show, but still nice for the user.

            p.kill()
            csvfile.close()
            outfile.close()
            if os.name == 'nt':
                os.remove(outfile.name)

            if parsed.nofile:
                os.remove(csvfile.name)

        else:
            print('Pinging %s...\nThe longer that this program runs, the larger the resulting CSV file will be.\nDue to'
                  ' the way that the program handles the output file, do not open the .csv file created by this '
                  'application until you are finished gathering pings.\nPress CNTRL+C to exit...' % parsed.address)

            csvfile, outfile = buildfiles(parsed.path, parsed.name)

            p = ping(parsed.address, customarg=parsed.gurusettings, ofile=outfile)

            try:
                while p.poll() is None:
                    row_generator = dataparser(outfile)
                    if row_generator is not None:
                        for row in row_generator:  # some code linters may read this as NoneType, this is handled...
                            writecsv(csvfile, row, terminaloutput=parsed.terminaloutput)
                    time.sleep(0.5)

            except (KeyboardInterrupt, SystemExit):
                p.kill()
                csvfile.close()
                outfile.close()
                if os.name == 'nt':
                    os.remove(outfile.name)
    elif parsed.plotfile is not None:
        showplot_fromfile(parsed.plotfile, parsed.generateimage)
    else:
        parser.print_usage()

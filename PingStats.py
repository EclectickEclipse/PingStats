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
effective a way as possible.

This software analyzes data recorded into CSV files by itself to either present an interactive plot (provided by the
Matplotlib package) or generate an image of a plot for specific logs.

This software also has the capability to display ping information as it is received, mapping it by time read and return
time of each packet read. When presenting information as it is received, the software does not write data to a CSV log,
instead relying on the use of the live presentation to present its information. It can however be instructed to output
information to a log for further usage for very minimal system resource cost. """

""" Technical Notes

It should be noted that the software inherently uses more system resources while displaying graphics to the screen, as
this software is intended to be run on as minimal a software as possible.

Due to the variance on OS dependent ping packages, data collection may not work, and may need tweaking. The
.dataparser() function is intended to be rewritten if possible. Due to this need to be easy to rewrite, the language is
as simplified as it can be, using only for loop structures and a few if statements. If you find the initially provided
code to be hard to interpret, uncomment the `# DEBUG:' lines to have python slowly iterate through each sequence of data
and show the results provided."""


# GPS discussion

# Record GPS coordinates from www.ipinfo.io requests whilst on non-mobile OS's.
# Plot a "heat map" of GPS coordinates and how fast/slow their connection was.

""" GPS Functionality Preamble
This software could be effectively used for mapping connection rate in various locations. This could allow the user
to map connection speeds throughout their city/region. This would be useful for people who move from location to
location on a regular basis, and require fast Internet connections everywhere they go.

Due to the variance in where this software could be used over time, it should be able to collect data from several
PingStatsLog.csv files and present them to the user overlaid on a map where the faster connections are presented as a
red "heat zones." """

""" GPS Functionality Technical notes
This software could use a kivy (see www.kivy.org) application to gather GPS coordinates. This would require a major
overhaul of the application structure, and should likely be handled in a fork.

The Kivy framework provides GPS functionality with Plyer (https://github.com/kivy/plyer), and provides a convienient
and well established framework for Multi-platform application development. Using this framework, the software could
easily provide a graphical presentation on the various options available to this software already."""


# GLOBALS
buildname = 'PingStats'
version = '1.0.04.2'
versiondate = 'Thu Aug  4 00:34:10 2016'
versionstr = 'PingStats Version %s (C) Ariana Giroux, Eclectick Media Solutions, circa %s' % (version, versiondate)

NT_ICMQSEQNUM = 0  # Used to ensure ICMQ sequence number consistency on NT based systems.


def buildfiles(path, name):
    """ Builds the files used for processing. For UNIX machines, generates a temporary file for ping output. Due to
    Temporary File limitations on Windows NT softwares, This function will generate a new folder in the install location
    of PingStats on the host OS.

    "path" - The path to output the CSV file to.
    "name" - The custom name supplied by the user.
    Returns a tuple containing the csv file object and the outbound data file object.
    """

    # First, convert args.

    if path is None:
        path = ''
    elif name is None:
        name = ''

    # Apply user arguments.

    if not parsed.nofile:
        try:
            dest = path + name + '.csv'
        except TypeError:
                sys.stderr.write('Could not parse specified arguments, defaulting to ./%sLog.csv\n' % buildname)

                dest = buildname + 'Log.csv'

    try:
        if not parsed.nofile:
            csvfile = open(dest, 'a+')  # actually open the CSV file at destination path.
    except OSError:
        raise RuntimeError('Please ensure that you use the full legal path to output the CSV file to.')

    if os.name == 'nt':  # Handle windows file creation.

        if os.getenv('LOCALAPPDATA', False):  # Check for LOCALAPPDATA environment variable.

            if os.access(os.getenv('LOCALAPPDATA'), os.F_OK):  # check for access to LOCALAPPDATA location.

                if not os.access(os.path.join(os.getenv('LOCALAPPDATA'), 'PingStats'), os.F_OK):  # If no folder exists
                    os.mkdir(os.path.join(os.getenv('LOCALAPPDATA'), 'PingStats'))  # Make new folder,
                    dfile = open(os.path.join(os.getenv('LOCALAPPDATA'), 'PingStats\\DataOutput.txt'), 'a+')  # build

                else:  # Implies that the PingStats folder exists.
                    dfile = open(os.path.join(os.getenv('LOCALAPPDATA'), 'PingStats\\DataOutput.txt'), 'a+')

            else:
                raise RuntimeError('FATAL ERROR! PINGSTATS COULD NOT ACCESS %LOCALAPPDATA%!!!')

        else:
            raise RuntimeError('FATAL ERROR! PINGSTATS COULD NOT ACCESS %LOCALAPPDATA%!!! \nExiting....\n')

    else:  # Handle *Nix file creation.
        dfile = tempfile.NamedTemporaryFile('w+')

    if not parsed.nofile:
        return csvfile, dfile  # return built files.
    else:
        return dfile


# TODO Initialize a CSV.writer object before execution of write_csv_data().
""" Currently, write_csv_data() initializes a new CSV.writer object every time it is called. This results in the program
working extra iterations on automatic garbage collection for the item.

The CSV.writer object only needs to be initialized once to maintain the functionality that we are looking for. The only
struggle will be getting the object into the runtime safely, without running into issues with threading buffer
overruns. """


def write_csv_data(file, data, terminal_output):
    """ Writes a row of CSV data.

    "file" - The file object to write to.
    "data" - The row to be saved.
    "terminal_output" - Boolean value to enable text output to the terminal.
    Returns the row written by the function.
    """
    cwriter = csv.writer(file)
    cwriter.writerow(data)
    rowtext = ''
    for val in data:
        rowtext += val + ', '
    if terminal_output:
        print('Wrote row: \'%s\' to %s' % (rowtext, file.name))


# TODO dataparser relies on potentially breakable parsing logic.
# TODO dataparser seems to be failing the row packing, and sometimes packs a row that is invalid.


def dataparser(datafile):
    """ Reads each line of data file for valid ping information, and once (or if) no new information is read, the
     function truncates the datafile and returns either a list of valid CSV rows, or an empty list object.

    "datafile" - The file to read for ping information.
    Returns a list of valid CSV rows for parsing by write_csv_data() or None when no new valid information is found.
    """

    datalist = []  # a list of rows read in by data parser.
    global NT_ICMQSEQNUM  # obtain ICMQ sequence counter.

    with open(datafile.name) as df:  # open the data file for reading

        for d in df:  # read datafile line by line, and parse lines for CSV output.
            # This is very logic heavy, and is not necessary to read through.
            data_row = [str(time.time())]
            # DEBUG: print("appended current system time to this data row"); time.sleep(1)

            # Parse data text
            if os.name != 'nt':
                # DEBUG: print("Determined a non NT system."); time.sleep(1)
                if d.lower().count('cannot resolve') > 0 or d.lower().count('request timeout'):
                    # DEBUG: print('read a line of text that contained \'cannot resolve\', appending data")
                    # DEBUG: time.sleep(1)
                    data_row.append('failed')  # Error line.
                    data_row.append('failed')
                    data_row.append('ICMQ_seq=%s' % d.split()[-1])
                    data_row.append('TTL=0')
                    data_row.append('time=-10')
                    # sys.stderr.write(str(data_row))

                elif (d.count('PING') > 0 or d.lower().count('statistics') > 0 or  # break on ping end.
                      d.lower().count('transmitted') > 0 or d.lower().count('round-trip') > 0):
                    pass

                else:
                    for val in d.split():  # Split lines by space and iterate.

                        if val.count('bytes') > 0 or val.count('from') > 0 or val.count('ms') > 0 or \
                                        val.count('\x00') > 0:  # skip-able values
                            pass

                        elif len(data_row) is 1:  # if this is the first data field.
                            data_row.append('size=%s' % val)

                        elif len(data_row) is 2:  # if this is the second data field.
                            data_row.append(val[:-1])

                        else:  # append data.
                            data_row.append(val)

            else:

                if d.lower().count('Request timed out.') > 1:
                    data_row.append('failed')
                    data_row.append('failed')
                    data_row.append('ICMQ_seq=%s' % NT_ICMQSEQNUM)
                    NT_ICMQSEQNUM += 1
                    data_row.append('TTL=0')
                    data_row.append('time-10')
                    # sys.stderr.write(data_row)

                elif d.lower().count('pinging') or d.lower().count('statistics') or d.lower().count('packets') or \
                        d.lower().count('approximate') or d.lower().count('minimum') or d.lower().count('control') or \
                        d.lower().count('^c') > 0:
                    pass

                else:
                    for val in d.split():

                        if val.lower().count('reply') or val.lower().count('from') > 0:
                            pass

                        elif val.lower().count('bytes') > 0:
                            data_row.insert(0, 'size=%s' % val.split('=')[1])

                        elif val.lower().count('time') > 0:
                            data_row.append(val)

                        elif val.lower().count('TTL') > 0:
                            data_row.insert(-2, val)

                        else:
                            data_row.append(val)

                    data_row.insert(2, 'ICMQ_seq=%s' % NT_ICMQSEQNUM)
                    NT_ICMQSEQNUM += 1

            # end parse

            # Check for row validity and append it to the list of read rows.
            if len(data_row) > 1:
                datalist.append(data_row)
            else:
                pass

    # data validity and size checks.
    if len(datalist) > 0:  # if data was found, return data and reduce file size.
        datafile.seek(0)
        datafile.truncate()

        # DEBUG
        # with open(datafile.name) as f:
        #     print(f.read())

        return datalist

    else:  # no data read, reduce file size, return an empty List object.
        datafile.seek(0)
        datafile.truncate()

        return []


def ping(address, custom_argument=None, out_file=None):
    """ Runs a ping and collects statistics.
    "address" - The address to ping.
    "custom_argument" - A string with user specified custom arguments.
    "out_file" - The file object to write output to.
    """

    # Address handler.
    if address is None:  # ensure a host was specified.
        sys.stderr.write('Please include at least one option...\nType -h for help...\n')
        quit()  # Break

    # Argument handler.
    if custom_argument is not None:
        safe_argument = ['ping', shlex.split(custom_argument), address]
    else:
        if os.name == 'nt':
            safe_argument = ['ping', '-t', address]
        else:
            safe_argument = ['ping', address]

    return subprocess.Popen(safe_argument, stdout=out_file)


# TODO Refactor .showliveplot() to a class.
""" .showliveplot() is looking more and more like a class. I feel like it is just prudent to refactor this to a
class. .showliveplot().PlotTable could simply be placed outside of the showliveplot function, and should still be
accessible by the name space.

For this function to work effectively for Kivy, we should use the matplotlib.garden to get an assigned number of plot
points from a class upon change to the class contents, like in the .showliveplot().PlotTable() object. """


def showliveplot(data_file, csv_file, refresh_frequency, table_length, no_file, terminaloutput):
    """ Shows a live graph of the last 50 rows of the specified CSV file on an interval of every half second.

    "data_file" - The file object used for data output.
    "csv_file" - The file object used for CSV output
    "refresh_frequency" - The frequency with which the matplotlib.animation.FuncAnimation object refreshes.
    "table_length" - The number of objects to maintain on screen.
    "no_file" - The option to not output to a file.
    Returns the matplotlib.animation.FuncAnimation object.
    """

    class PlotTable:
        """ A class to maintain a specified number of objects to plot to matplotlib. """

        def __init__(self, length):
            self.x = []
            self.y = []

            if length is None:
                self.length = 50
            else:
                self.length = int(table_length)

        def appendx(self, a):
            """ Append a new value to the x value of the table. Maintains specified length of table upon reaching max.

            "a" - The value to append to the table.
            """
            if len(self.x) < self.length:
                self.x.append(a)
            else:
                self.x.pop(0)
                self.x.append(a)

        def appendy(self, a):
            """ Append a new value to the y value of the table. Maintains specified length of table upon reaching max.

            "a" - The value to append to the table.
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

    # build argument string for window title string
    title_string = ''
    for arg in sys.argv:
        if sys.argv.index(arg) is 0:
            pass
        else:
            title_string += ' ' + arg
    fig.canvas.set_window_title('%s |%s' % (buildname + ' ' + version, title_string))

    ax1 = fig.add_subplot(1, 1, 1)

    ptable = PlotTable(table_length)

    def animate(i):
        """ Reads rows from a CSV file and render them to a plot.

        "i" - Required by matplotlib.animation.FuncAnimation
        Returns None.
        """

        data_generator = dataparser(data_file)
        if data_generator is not None:
            for newrow in data_generator:  # some code linter's may read this as NoneType, this is handled...
                if not no_file:
                    write_csv_data(csv_file, newrow, terminaloutput)
                elif terminaloutput:
                    print(newrow)
                ptable.appendx(dt.datetime.fromtimestamp(float(newrow[0])))
                ptable.appendy(newrow[5].split('=')[1])

        ax1.clear()
        ax1.plot_date(ptable.getx(), ptable.gety(), '-', label='Connection over time')
        ax1.plot(ptable.getx(), ptable.gety())
        for label in ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        plt.xlabel('Timestamps')
        plt.ylabel('Return Time (in milliseconds)')
        plt.title('Ping Over Time')

    plt.subplots_adjust(left=0.13, bottom=0.33, right=0.95, top=0.89)
    print('Showing plot...\n')

    if refresh_frequency is None:
        ani = animation.FuncAnimation(fig, animate, interval=500)
    else:
        ani = animation.FuncAnimation(fig, animate, interval=int(refresh_frequency))

    ani.new_frame_seq()
    plt.show()

    return True


def showplot_fromfile(csv_file_path, image_name):
    """ Generates a plot from a csv file specified by the user. Also generates images of the file by supplying an
    image name parameter.

    "csv_file_path" - The path to the file to generate.
    "image_name" - Optional argument to specify an image to generate.
    """
    style.use('fivethirtyeight')

    fig = plt.figure()

    # build argument string for window title string
    title_string = ''
    for arg in sys.argv:
        if sys.argv.index(arg) is 0:
            pass
        else:
            title_string += ' ' + arg
    fig.canvas.set_window_title('%s |%s' % (buildname + ' ' + version, title_string))

    ax1 = fig.add_subplot(1, 1, 1)

    table = []

    print('Reading ping information from user specified file.')
    with open(csv_file_path) as cf:
        creader = csv.reader(cf)
        for line in creader:
            table.append(line)

    x = []
    y = []

    for i, newrow in enumerate(table):
        # print(newrow)  # DEBUG
        try:
            x.append(dt.datetime.fromtimestamp(float(newrow[0])))
            y.append(newrow[5].split('=')[1])
        except IndexError as e:
            print('Could not read line #%s %s, python threw $s!' % (i + 1, newrow, e))

    ax1.plot(x, y)

    plt.subplots_adjust(left=0.13, bottom=0.33, right=0.95, top=0.89)

    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)

    plt.xlabel('Timestamps')
    plt.ylabel('Return Time (in milliseconds)')
    plt.title('Ping Over Time')

    if image_name is not None:  # User flagged -gi, generate an image.
        print('Generating %s.png.' % image_name)
        plt.savefig('%s.png' % image_name)
    else:  # Display plot.
        print('Showing the plot generated from \"%s.\"' % csv_file_path)
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
                                                          'of the -s plot visualization feature. The lower the number,'
                                                          'the better the performance of %s visualization. Handy for'
                                                          '\"potatoes\"' % buildname)

    parser.add_argument('-sL', '--tablelength', help='The total number of pings to show for -s. The lower the number, '
                                                     'the better the performance of %s visualization. Handy for '
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
                  'consider using the live plotting feature for shorter run times (i.e a match of on line chess).\n'
                  'Close the plot window to exit the program....' % parsed.address)

            csvfile, outfile = buildfiles(parsed.path, parsed.name)

            p = ping(parsed.address, custom_argument=parsed.gurusettings, out_file=outfile)

            # hangs while showing a plot, when user closes plot, process closes.file.name)
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
                  'application until you are finished gathering pings.\nPress CTR+C to exit...' % parsed.address)

            csvfile, outfile = buildfiles(parsed.path, parsed.name)

            p = ping(parsed.address, custom_argument=parsed.gurusettings, out_file=outfile)

            try:
                while p.poll() is None:
                    row_generator = dataparser(outfile)
                    if row_generator is not None:
                        for row in row_generator:  # some code linter's may read this as NoneType, this is handled...
                            write_csv_data(csvfile, row, terminal_output=parsed.terminaloutput)
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

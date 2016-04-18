#! /Library/Frameworks/Python.framework/Versions/3.5/bin/python3.5

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
# TODO Further document bugs.
# TODO Further document preamble.

version = '0.07.03a'
versiondate = 'Sun Apr 17 15:24:43 2016'
versionstr = 'PingStats Version %s (C) Ariana Giroux, Eclectick Media Solutions, circa %s' % (version, versiondate)


# Run the main functionality.

def ping(address, customarg=None, wait=None, path=None, name=None, nofile=False, pingfrequency=60):
    # TODO Build parameter checks into function, make bootstrap easier to read. Its getting very excessive.
    """ Runs a ping and collects statistics.
    :param address: The address to ping.
    :param customarg: A string with user specified custom arguments.
    :param wait: An integer value specifying how long to wait.
    :param path: A path to output files.
    :param name: Use a custom name for the CSV output.
    :param nofile: Flag this option to disable CSV output.
    :param pingfrequency: The amount of time between spawning new ping processi.
    """
    if address is None:  # ensure a host was specified.
        print('Please include at least one option...\nType -h for help...')
        quit()  # Break

    def parsearg(custom_argument):
        """ Creates an argument for the subprocess.Popen object.

        :param custom_argument: The custom argument specified by the user (or None for no custom argument)
        :return: A mutable list containing the argument to use in the subprocess.Popen object.
        """
        if custom_argument is not None:
            return ['ping', shlex.split(custom_argument), address]
        else:
            return ['ping', '-c 1', address]

    def ping(argument, file):
        """ Pings a host.

        :param argument: A mutable list to use for the subprocess.Popen object.
        :param file: An output file.
        :return: The process object.
        """
        return subprocess.Popen(argument, stdout=file)

    def buildfiles(path, name=None):
        """ Builds the files used for processing.

        :param path: The path to output the files to.
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
                    csvfile = open('%s%s-%s.csv' % (path, address, time.ctime()), 'w+')
                    outfile = open('%sout.txt' % path, 'w+')
                    return csvfile, outfile
                else:
                    csvfile = open('%s-%s.csv' % (address, time.ctime()), 'w+')
                    outfile = open('out.txt', 'w+')
                    return csvfile, outfile
        except OSError as e:
            print('Please ensure you have included a legal path!\n%s, %s' % (e.errno, e.strerror))
            quit()  # break

    csvfile, outfile = buildfiles(path, name)

    def writeCsv(file, row):
        """ Writes a row of CSV data.

        :param file: The file object to write to.
        :param row: The row to be saved.
        :return: The file object passed to the function.
        """
        cwriter = csv.writer(file)
        cwriter.writerow(row)
        return row

    def dataparser(datafile):
        """Parses through lines of text returned by ping and further refines it.

        :param datafile: The position of the log file to read.
        :return: The lines read.
        """
        for data in datafile:
            row = [time.time(), ]
            if data.lower().count('cannot resolve') > 0 or data.lower().count('request timeout'):
                row.append(data)
            elif (data.count('PING') > 0 or data.lower().count('statistics') > 0 or
                  data.lower().count('transmitted') > 0 or data.lower().count('round-trip') > 0):  # Break on ping end.
                pass
            else:
                for val in data.split():  # Split lines by space and iterate.
                    if val.count('bytes') > 0 or val.count('from')  > 0 or val.count('ms') > 0 or \
                                    val.count('\x00') > 0:  # skippable values
                        pass
                    elif len(row) is 1:  # if this is the first data field.
                        row.append('size=%s' % val)
                    elif len(row) is 2:  # if this is the second data field.
                        row.append(val[:-1])
                    else:  # append data.
                        row.append(val)
                if len(row) > 1:
                    yield row

    # Main Logic
    # TODO Restructure main logic to parse program arguments.

    try:  # catch keyboard interrupts and system exits, ensure CSV data is saved.

        if type(wait) is int:  # if user specified to wait for time.
            print('Pinging %s for %s seconds.\nThe longer the time pings are sent for, the larger the resulting CSV '
                  'file will be.' % (address, wait))
            totaltime = 0
            while totaltime < wait:
                timestart = time.time()

                process = ping(parsearg(customarg), outfile)
                time.sleep(pingfrequency)  # hang to ensure user specified ping frequency.
                while process.poll() is None:
                    pass  # hang for process competion.

                if not nofile:
                    with open(outfile.name) as datafile:
                        for row in dataparser(datafile):
                            writeCsv(csvfile, row)

                totaltime += time.time() - timestart

            else:
                if not nofile:
                    print('Quiting Ping and saving stats to a CSV file.')
                    with open(outfile.name) as datafile:
                        for row in dataparser(datafile):
                            writeCsv(csvfile, row)

        else:  # else ping.
            print('Pinging %s...\nThe longer that this program runs, the larger the resulting CSV file will be.\n'
                  'Press CNTRL+C to exit...' % address)

            processes = []

            while 1:
                try:  # catch keyboard interrupts and system exits, ensure CSV data is saved.

                    process = ping(parsearg(customarg), outfile)
                    processes.append(process)
                    time.sleep(pingfrequency)  # hang to ensure user specified ping frequency.
                    while process.poll() is None:
                        pass  # hang for process competion.

                    if not nofile:
                        with open(outfile.name) as datafile:
                            for row in dataparser(datafile):
                                writeCsv(csvfile, row)

                except (KeyboardInterrupt, SystemExit):
                    print('Quiting Ping and saving stats to a CSV file.')
                    try:
                        for p in processes:
                            p.kill()
                    except OSError as e:
                        if e.errno is 3:
                            pass
                        else:
                            raise e

                    if not nofile:
                        with open(outfile.name) as datafile:
                            for row in dataparser(datafile):
                                writeCsv(csvfile, row)

                    break

    except (KeyboardInterrupt, SystemExit):
        print('Quiting Ping and saving stats to a CSV file.')
        if not nofile:
            with open(outfile.name) as datafile:
                for row in dataparser(datafile):
                    writeCsv(csvfile, row)
        return 1

    # Close files and delete logfile.
    outfile.close()
    csvfile.close()
    os.remove(outfile.name)

    # return exit code
    return 0


# Read CSV logs.

def read(filepos):
    # TODO Further define read90
    """ Parses through a PingStats generated CSV file.

    :param filepos: The position of the file.
    :return:
    """
    # Row structure is as follows.
    # SIZE,ADDRESS:,ICMP_SEQ,TTL,TIME
    try:  # catch OSErrors

        with open(filepos) as f:  # open user specified file for parsing.
            print("Reading given CSV file...")
            creader = csv.reader(f)
            table = {}
            success = {}
            failed = {}
            # refined stats
            ttls = {}
            ttlssum = 0  # for maths
            times = {}
            timessum = 0  # for maths

            for i, row in enumerate(creader):  # build table.
                table[i] = row
                if len(row) == 1 or row.count('cannot resolve') or row.count('request timeout') > 1:  # catch failed
                    failed[i] = row
                else:
                    success[i] = row

            address = table[0][2]  # Grab the address used in the read.

            for key in success:  # build ttls
                try:
                    ttlssum += float(success[key][-2].split('=')[1])
                    ttls[key] = success[key][-2].split('=')[1]
                except IndexError:
                    pass

            for key in success:  # build times
                try:
                    timessum += float(success[key][-1].split('=')[1])
                    times[key] = success[key][-1].split('=')[1]
                except IndexError:
                    pass

            print('Calculating percentages...')
            psuccess = (1.0 * (len(success) / len(table)) * 100)
            pfailed = (1.0 * (len(failed) / len(table)) * 100)


            averagettl = 1.0 * (ttlssum / len(ttls))
            averagetime = 1.0 * (timessum / len(times))

            def makeplot():
                # TODO Populate list of minutes elapsed
                # TODO Define animation function.
                # Should this be its own function? Possibly class? Use of matplotlib inherently makes this "function"
                # hard to call a function. I feel as if it would be best to use an object instead. This would provide
                # easier modification and interaction later down the line.
                style.use('fivethirtyeight')

                fig = plt.figure()
                ax1 = fig.add_subplot(1,1,1)

                def getvalues():
                    for val in ttls:
                        yield ttls[val], success[val][0]

                def animate(i):
                    timestart = table[0][0]
                    x, raw_y = getvalues()
                    y = raw_y - timestart / 60
                    ax1.clear()
                    ax1.plot(x, y)

                # TODO BUG MakeplotMissingFrame: read.makeplot() does not show a plot, and does not hang for animation.
                ani = animation.FuncAnimation(fig, animate, interval=1000)
                # DEBUG
                # sys.stderr.write('Showing plot \n')
                plt.show()

            makeplot()

            return 0

    except OSError as e:
        print('Please ensure you have included a valid file path....\n%s, %s' % (e.errno, e.strerror))
        return 1


# Get version variables

def getversion():
    return versionstr


# Bootstrap logic.

if __name__ == '__main__':
    # Define program arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', help='The IP address to ping.')
    parser.add_argument('-c', '--customarg', help='Define your own argument for the ping.'
                                                  'If you are experiencing issues with pings ending before intended,'
                                                  'try using \'-c \"-c 999999999\"\' to spawn a process with an '
                                                  'extremely long runtime.')
    parser.add_argument('-d', '--destination', help='To supply a specific path to output any files to, include a path.')
    parser.add_argument('-F', '--pingfrequency', help='The frequency with which to ping the host. Defaults to 0.25 '
                                                      'seconds.')
    parser.add_argument('-n', '--name', help='Flag this option to use a custom name for the CSV output file.')
    parser.add_argument('-r', '--readfile', help='Flag this option and the path to a csv file containing ping '
                                                 'statistics, and this program will provide various options for '
                                                 'breaking down the statistics of the pings.')
    parser.add_argument('-t', '--time', help='The time to wait before killing the process in seconds.')
    parser.add_argument('-v', '--version', help='Flag this option to display software version.', action='store_true')
    parser.add_argument('-V', '--verbose', help='Flag this option for verbosity during option parsing logic.',
                        action='store_true')
    parser.add_argument('--debug', help='Flag this to enable debugging. As of 1.5, it prevents the program from '
                                        'outputting a CSV file.', action='store_true')
    parsed = parser.parse_args()

    # Parse argument logic for ping().
    # TODO BUG BootstrapperLogic: Documenting all of the ways the bootstrap logic tree fails would'nt be worth the time.
    # TODO BUG BootstrapperLogic: Bootstrap logic currently fails on destination designation.
    # Seriously tho. Why is the program doing any of this? It could just as easily pass the parsed args to ping() and
    # read() respectively.
    sys.stderr.write("\nAs of Version %s, this program does not have very good functionality outside of pinging "
                     "addresses. I.e, -t produces a working ping, but does not hang for time.\nThis requires a major "
                     "restructuring of the \'if __name__ == \'__main__\':\' boostrapping logic.\nThis is coming in "
                     "version 1.07.04a(ish(c)).\n\n" % version)
    if parsed.readfile is None and not parsed.version:  # If not single operation options,

        if parsed.address is not None:  # address
            if parsed.verbose:
                print('have address')

            if parsed.destination is not None:  # address, destination
                if parsed.verbose:
                    print('have destination')

                if parsed.name is not None:  # address, destination, name
                    if parsed.verbose:
                        print('have name')

                    if parsed.time is not None:  # address, destination, name, time
                        if parsed.verbose:
                            print('have time')

                        if parsed.pingfrequency is not None:  # address, destination, name, time, pingfrequency
                            if parsed.verbose:
                                print('have frequency')

                            if parsed.customarg is not None:  # address, destination, name, time, pingfrequency, arg
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, wait=int(parsed.time),
                                     path=parsed.destination, name=parsed.name, pingfrequency=int(parsed.pingfrequency))

                            else:  # address, destination, name time, pingfrequency

                                ping(parsed.address, wait=int(parsed.time), path=parsed.destination, name=parsed.name,
                                     pingfrequency=int(parsed.pingfrequency))

                        else:

                            if parsed.customarg is not None:  # address, destination, name, time, argument
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, wait=int(parsed.time),
                                     path=parsed.destination, name=parsed.name)

                            else:  # address, destination, name, time

                                ping(parsed.address, wait=int(parsed.time), path=parsed.destination, name=parsed.name,
                                     nofile=parsed.debug)

                    else:  # address, destination, name

                        if parsed.pingfrequency is not None:  # address, destination, name, pingfrequency
                            if parsed.verbose:
                                print('have frequency')

                            if parsed.customarg is not None:  # address, destination, name, pingfrequency, arg
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, path=parsed.destination,
                                     name=parsed.name, pingfrequency=int(parsed.pingfrequency))

                            else:  # address, destination, name pingfrequency

                                ping(parsed.address, path=parsed.destination, name=parsed.name,
                                     pingfrequency=int(parsed.pingfrequency))
                        else:

                            if parsed.customarg is not None:  # address, destination, name, time, argument
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, path=parsed.destination,
                                     name=parsed.name)

                            else:  # address, destination, name

                                ping(parsed.address, path=parsed.destination, name=parsed.name, nofile=parsed.debug)

                else:  # address, destination
                    if parsed.time is not None:  # address, destination, time
                        if parsed.verbose:
                            print('have time')

                        if parsed.pingfrequency is not None:  # address, destination time, pingfrequency
                            if parsed.verbose:
                                print('have frequency')

                            if parsed.customarg is not None:  # address, destination, time, pingfrequency, arg
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, wait=int(parsed.time),
                                     path=parsed.destination, pingfrequency=int(parsed.pingfrequency))

                            else:  # address, destination, time, pingfrequency

                                ping(parsed.address, wait=int(parsed.time), path=parsed.destination,
                                     pingfrequency=int(parsed.pingfrequency))

                        else:

                            if parsed.customarg is not None:  # address, destination, time, argument
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, wait=int(parsed.time),
                                     path=parsed.destination, name=parsed.name)

                            else:  # address, destination
                                ping(parsed.address, path=parsed.destination)

            else:  # address
                if parsed.name is not None:  # address, name
                    if parsed.verbose:
                        print('have name')

                    if parsed.time is not None:  # address, name, time
                        if parsed.verbose:
                            print('have time')

                        if parsed.pingfrequency is not None:  # address, name, time, pingfrequency
                            if parsed.verbose:
                                print('have frequency')

                            if parsed.customarg is not None:  # address, name, time, pingfrequency, arg
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, wait=int(parsed.time),
                                     name=parsed.name, pingfrequency=int(parsed.pingfrequency))

                            else:  # address, name time, pingfrequency

                                ping(parsed.address, wait=int(parsed.time), name=parsed.name,
                                     pingfrequency=int(parsed.pingfrequency))
                        else:

                            if parsed.customarg is not None:  # address, name, time, argument
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, wait=int(parsed.time), name=parsed.name)

                            else:  # address, name, time

                                ping(parsed.address, wait=int(parsed.time), name=parsed.name, nofile=parsed.debug)

                    else:  # address, name

                        if parsed.pingfrequency is not None:  # address, name, pingfrequency
                            if parsed.verbose:
                                print('have frequency')

                            if parsed.customarg is not None:  # address, name, pingfrequency, arg
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, name=parsed.name,
                                     pingfrequency=int(parsed.pingfrequency))

                            else:  # address, name pingfrequency

                                ping(parsed.address, name=parsed.name, pingfrequency=int(parsed.pingfrequency))

                        else:

                            if parsed.customarg is not None:  # address, name, time, argument
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, name=parsed.name)

                            else:  # address, name

                                ping(parsed.address, name=parsed.name, nofile=parsed.debug)

                else:  # address
                    if parsed.time is not None:  # address, name, time
                        if parsed.verbose:
                            print('have time')

                        if parsed.pingfrequency is not None:  # address, name, time, pingfrequency
                            if parsed.verbose:
                                print('have frequency')

                            if parsed.customarg is not None:  # address, name, time, pingfrequency, arg
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, wait=int(parsed.time),
                                     name=parsed.name, pingfrequency=int(parsed.pingfrequency))

                            else:  # address, name time, pingfrequency

                                ping(parsed.address, wait=int(parsed.time), name=parsed.name,
                                     pingfrequency=int(parsed.pingfrequency))
                        else:

                            if parsed.customarg is not None:  # address, name, time, argument
                                if parsed.verbose:
                                    print('have customarg')

                                ping(parsed.address, customarg=parsed.customarg, wait=int(parsed.time), name=parsed.name)

                            else:  # address, name, time

                                ping(parsed.address, wait=int(parsed.time), name=parsed.name, nofile=parsed.debug)

                    else:  # address
                        ping(parsed.address)

        else:  # No address, requires at least an address to use ping()
            print('Please include an address with the -a flag...\nUse -h for help...')

    else:  # Parse arguments for read() and getversion()
        if parsed.readfile is not None:
            read(parsed.readfile)
        elif parsed.version:
            print(getversion())
        else:
            print('Please include an address with the -a flag...\nUse -h for help...')

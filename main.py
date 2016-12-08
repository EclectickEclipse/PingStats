import core
import Plot
import argparse
import csv
import atexit

parser = argparse.ArgumentParser(
    description='%s. This program defines some basic ping statistic '
                'visualizationmethods through Python\'s \'matplotlib\'.'
                % core.versionstr)

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
                    'the last 500 ping sequences.', action='store_true')

parser.add_argument('-sF', '--refreshfrequency',
                    help='Specify a number of milliseconds to wait between'
                    'refreshes of the -s plot visualization feature.'
                    'The lower the number, the better the performance'
                    'of %s visualization. Handy for \"potatoes\"'
                    % core.buildname)

parser.add_argument('-sL', '--tablelength',
                    help='The total number of pings to show for -s. The'
                    'lower the number, the better the performance of '
                    '%s visualization. Handy for \"potatoes.\"'
                    % core.buildname)

parser.add_argument('-sNF', '--nofile',
                    help='Flag this option to disable outputting ping '
                    'information to a csv  file during live plotting.'
                    ' Helps with memory consumption.', action='store_true')

parser.add_argument('-v', '--version',
                    help='Flag this option to display software version.',
                    action='store_true')

parsed = parser.parse_args()

if parsed.version:
    print(core.versionstr)
elif parsed.address is not None:
    if parsed.showliveplot:
        cwriter = None

        if not parsed.nofile:
            cwriter = csv.writer(core.buildfile(parsed.path, parsed.name))

        p = core.ping(parsed.address)
        plot = Plot.Animate(p, parsed.tablelength, parsed.refreshfrequency)
        plot.animate()

        atexit.register(plot.close_thread)
    else:
        if not parsed.nofile:
            cwriter = csv.writer(core.buildfile(parsed.path, parsed.name))

        for return_tuple in core.ping(parsed.address):
            if not parsed.nofile:
                core.write_csv_data(cwriter, return_tuple)

elif parsed.plotfile is not None:
    Plot.PlotFile(parsed.plotfile)
else:
    parser.print_useage()

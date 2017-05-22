import core
import plot
import argparse
import time

from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2TkAgg
import matplotlib.animation as animation

parser = argparse.ArgumentParser(
    description='%s. This program defines some basic ping statistic '
                'visualizationmethods through Python\'s \'matplotlib\'.'
                % core.versionstr)

parser.add_argument('-a', '--address', help='The IP address to ping.')

parser.add_argument('-d', '--delay', help='The interval of time (in seconds'
                    ') to wait between ping requests.', type=float,
                    default=0.22)

parser.add_argument('-gi', '--generateimage',
                    help='Used in conjunction with the -pf option, this '
                    'option sends a name for a \'*.png\' file to save'
                    ' to the current working directory.')

parser.add_argument('-n', '--name',
                    help='Flag this option to use a custom name for the'
                    ' CSV output file.')

parser.add_argument('-p', '--path',
                    help='The path to output csv files to')

parser.add_argument('-pf', '--plotfile',
                    help='Include the path to a previously generated CSV'
                    'file to generate a plot.')

parser.add_argument('-q', '--quiet', help='Flag this for quiet operation.',
                    action='store_true')

parser.add_argument('-s', '--showliveplot',
                    help='Flag this option to display an animated plot of'
                    'the last 500 ping sequences.', action='store_true')

parser.add_argument('-sF', '--refreshfrequency',
                    type=float,
                    help='Specify a number of milliseconds to wait between'
                    'refreshes of the -s plot visualization feature.'
                    'The lower the number, the better the performance'
                    'of %s visualization. Handy for \"potatoes\"'
                    % core.buildname)

parser.add_argument('-sL', '--tablelength',
                    type=int,
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


def _quit():
    root.quit()
    root.destroy()

if parsed.version:
    print(core.versionstr)

elif parsed.address is not None:

    if parsed.showliveplot:
        root = Tk()
        p = plot.Animate(root,
                         core.Core(parsed.address, parsed.path, parsed.name,
                                   parsed.nofile, not parsed.quiet
                                   ).ping_generator,
                         table_length=parsed.tablelength
                         )

        p.pack(side=BOTTOM, fill=BOTH)

        if parsed.refreshfrequency is None:
            ani = animation.FuncAnimation(p.fig, p.animate,
                                          interval=1000)
        else:
            ani = animation.FuncAnimation(p.fig, p.animate,
                                          interval=parsed.refreshfrequency)

        button = Button(root, text='Quit', command=_quit)
        button.pack(side=BOTTOM)

        root.mainloop()

    else:
        c = core.Core(parsed.address, parsed.path, parsed.name,
                      parsed.nofile, parsed.quiet)

        for return_data in c.ping_generator:
            if not c.nofile:
                core.write_csv_data(c.cwriter, return_data)

            time.sleep(parsed.delay)

elif parsed.plotfile is not None:
    pf = plot.PlotFile(parsed.plotfile, parsed.generateimage)
    pf.get_figure()
else:
    parser.print_help()

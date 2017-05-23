import core
import plot
import argparse
import time

from tkinter import *
from tkinter import ttk
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


class Main(Tk):
    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)

        # PING SETTINGS
        self.ping_settings = PingSettings(self)
        self.ping_settings.pack(pady=10)

        # FILE SETTINGS
        self.file_settings = FileSettings(self)
        self.file_settings.pack(pady=10)

        # PLOT SETTINGS
        self.plot_settings = PlotSettings(self)
        self.plot_settings.pack(pady=10)

        self.run = Button(self, text='Start ping and display plot',
                          command=self.start_ping)
        self.run.pack(side=BOTTOM)

    def start_ping(self):
        address, delay, timeout = self.ping_settings.get_values()
        name, path, write = self.file_settings.get_values()
        frequency, length = self.plot_settings.get_values()


class PingSettings(ttk.Frame):
    def __init__(self, root, **kwargs):
        super(PingSettings, self).__init__(root, **kwargs)
        Label(self, text='Ping Settings').grid(row=0, columnspan=2)

        Label(self, text='Address:').grid(row=1, column=0)
        if parsed.address is not None:
            self.address_entry = Entry(self, text=parsed.address)
        else:
            self.address_entry = Entry(self)
        self.address_entry.grid(row=1, column=1)

        Label(self, text='Delay between pings:').grid(row=2, column=0)
        self.delay_entry = Entry(self, text=str(parsed.delay))
        self.delay_entry.grid(row=2, column=1)

        Label(self, text='Timeout:').grid(row=3, column=0)
        self.timeout_entry = Entry(self)
        self.timeout_entry.grid(row=3, column=1)

    def get_values(self):
        return (self.address_entry.get(), self.delay_entry.get(),
                self.timeout_entry.get())


class FileSettings(ttk.Frame):
    def __init__(self, root, **kwargs):
        super(FileSettings, self).__init__(root, **kwargs)
        Label(self, text='CSV File Settings').grid(row=0, columnspan=2)

        Label(self, text='File Name:').grid(row=1, column=0)
        if parsed.name is not None:
            self.name_entry = Entry(self, text=parsed.name)
        else:
            self.name_entry = Entry(self, text='PingStatsLog')
        self.name_entry.grid(row=1, column=1)

        Label(self, text='File Path:').grid(row=2, column=0)
        self.path_entry = Entry(self, text=parsed.path)
        self.path_entry.grid(row=2, column=1)

        self.write_file = BooleanVar()
        self.write_file.set(not parsed.nofile)
        Checkbutton(self, text='Write CSV file',
                    variable=self.write_file).grid(row=3, columnspan=2)

    def get_values(self):
        return (self.name_entry.get(), self.path_entry.get(),
                self.write_file.get())


class PlotSettings(ttk.Frame):
    def __init__(self, root, **kwargs):
        super(PlotSettings, self).__init__(root, **kwargs)
        Label(self, text='Plot Settings').grid(row=0, columnspan=2)

        Label(self, text='Plot refresh frequency, in milliseconds:').grid(
            row=1, column=0
        )
        if parsed.refreshfrequency is not None:
            self.frequency_entry = Entry(self,
                                         text=str(parsed.refreshfrequency))
        else:
            self.frequency_entry = Entry(self)
        self.frequency_entry.grid(row=1, column=1)

        Label(self, text='Number of points to display:').grid(row=2, column=0)
        if parsed.tablelength is not None:
            self.length_entry = Entry(self, text=str(parsed.tablelength))
        else:
            self.length_entry = Entry(self)
        self.length_entry.grid(row=2, column=1)

    def get_values(self):
        return self.frequency_entry.get(), self.length_entry.get()


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

if __name__ == '__main__':
    root = Main()
    root.mainloop()

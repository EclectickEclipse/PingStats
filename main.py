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

parser.add_argument('-d', '--delay', help='The interval of time (in seconds) '
                                          'to wait between ping requests.',
                    type=float,
                    default=0.22)

parser.add_argument('-t', '--timeout',
                    help='The amount of time to set for each packets\' '
                         'timeout.',
                    type=int, default=3000)

parser.add_argument('-gi', '--generateimage',
                    help='Used in conjunction with the -pf option, this '
                    'option sends a name for a \'*.png\' file to save'
                    ' to the current working directory.')

parser.add_argument('-n', '--name',
                    default=core.buildname + 'Log',
                    help='Flag this option to use a custom name for the'
                    ' CSV output file.')

parser.add_argument('-p', '--path',
                    default='',
                    help='The path to output csv files to')

parser.add_argument('-pf', '--plotfile',
                    help='Include the path to a previously generated CSV'
                    'file to generate a plot.')

parser.add_argument('-q', '--quiet', help='Flag this for quiet operation.',
                    action='store_true')

parser.add_argument('-s', '--showliveplot',
                    help='Flag this option to display a live plot of return '
                         'time (in ms) by time received. Use this command to '
                         'skip the UI entirely.', action='store_true')

parser.add_argument('-c', '--cli',
                    help='Flag this option if you want to skip running the UI '
                         'entirely, and instead just rely on CLI arguments.',
                    action='store_true')

parser.add_argument('-sF', '--refreshfrequency',
                    type=float, default=1000,
                    help='Specify a number of milliseconds to wait between'
                    'refreshes of the -s plot visualization feature.'
                    'The lower the number, the better the performance'
                    'of %s visualization. Handy for \"potatoes\"'
                    % core.buildname)

parser.add_argument('-sL', '--tablelength',
                    type=int, default=250,
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


def _quit():  # used by -s
    root.quit()
    root.destroy()


class Main(Tk):
    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)
        # tk.Tk.__init__(self, *args, **kwargs)
        container = ttk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        self.frames = {
            Settings: Settings(container, self),
            Plot: Plot(container, self),
        }

        for F in self.frames:
            self.frames[F].grid(row=0, column=0, sticky="nsew")

        self.show_settings()

    def show_settings(self):
        self.frames[Settings].tkraise()

    def show_plot(self, ping, file, plot):
        self.frames[Plot].generate_plot(ping, file, plot)
        self.frames[Plot].tkraise()


class Settings(ttk.Frame):
    def __init__(self, parent, controller):
        super(Settings, self).__init__(parent)

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
                          command=lambda: controller.show_plot(
                              self.ping_settings.get_values(),
                              self.file_settings.get_values(),
                              self.plot_settings.get_values()
                          ))
        self.run.pack(side=BOTTOM)


class PingSettings(ttk.Frame):
    def __init__(self, root, **kwargs):
        super(PingSettings, self).__init__(root, **kwargs)
        Label(self, text='Ping Settings').grid(row=0, columnspan=2)

        Label(self, text='Address:').grid(row=1, column=0)
        if parsed.address is not None:
            self.address_entry = Entry(self)
            self.address_entry.insert(0, parsed.address)
        else:
            self.address_entry = Entry(self)
        self.address_entry.grid(row=1, column=1)

        Label(self, text='Delay between pings:').grid(row=2, column=0)
        self.delay_entry = Entry(self)
        self.delay_entry.insert(0, str(parsed.delay))
        self.delay_entry.grid(row=2, column=1)

        Label(self, text='Timeout:').grid(row=3, column=0)
        self.timeout_entry = Entry(self)
        self.timeout_entry.insert(0, str(parsed.timeout))
        self.timeout_entry.grid(row=3, column=1)

    def get_values(self):
        return (self.address_entry.get(), self.delay_entry.get(),
                self.timeout_entry.get())


class FileSettings(ttk.Frame):
    def __init__(self, root, **kwargs):
        super(FileSettings, self).__init__(root, **kwargs)
        Label(self, text='CSV File Settings').grid(row=0, columnspan=2)

        Label(self, text='File Name:').grid(row=1, column=0)
        self.name_entry = Entry(self)
        self.name_entry.insert(0, parsed.name)
        self.name_entry.grid(row=1, column=1)

        Label(self, text='File Path:').grid(row=2, column=0)
        self.path_entry = Entry(self)
        self.path_entry.insert(0, parsed.path)
        self.path_entry.grid(row=2, column=1)

        self.write_file = BooleanVar(value=not parsed.nofile)
        Checkbutton(self, text='Write CSV file',
                    variable=self.write_file).grid(row=3, columnspan=2)

    def get_values(self):
        print(self.write_file.get())
        return (self.name_entry.get(), self.path_entry.get(),
                self.write_file.get())


class PlotSettings(ttk.Frame):
    def __init__(self, root, **kwargs):
        super(PlotSettings, self).__init__(root, **kwargs)
        Label(self, text='Plot Settings').grid(row=0, columnspan=2)

        Label(self, text='Plot refresh frequency, in milliseconds:').grid(
            row=1, column=0
        )
        self.frequency_entry = Entry(self)
        self.frequency_entry.insert(0, str(parsed.refreshfrequency))
        self.frequency_entry.grid(row=1, column=1)

        Label(self, text='Number of points to display:').grid(row=2, column=0)
        self.length_entry = Entry(self)
        self.length_entry.insert(0, str(parsed.tablelength))
        self.length_entry.grid(row=2, column=1)

    def get_values(self):
        return self.frequency_entry.get(), self.length_entry.get()


class Plot(ttk.Frame):
    def __init__(self, parent, controller):
        super(Plot, self).__init__(parent)

        button = Button(self, text='Stop ping and return to settings.',
                        command=lambda: self.destroy_and_return(controller))
        button.pack(side=BOTTOM)

        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack()

        self.p = None
        self.ani = None

    def generate_plot(self, ping_tuple, file_tuple, plot_tuple):
        address, delay, timeout = ping_tuple
        name, path, write = file_tuple
        frequency, length = plot_tuple

        delay = float(delay)
        timeout = int(timeout)
        frequency = float(frequency)
        length = int(length)

        self.p = plot.Animate(self.plot_frame,
                              core.Core(address, path, name, not write,
                                        not parsed.quiet, delay,
                                        timeout=timeout),
                              table_length=length)
        self.p.pack(side=TOP, fill=BOTH)

        self.ani = animation.FuncAnimation(self.p.fig, self.p.animate,
                                           interval=frequency)

    def destroy_and_return(self, controller):
        self.p.destroy()
        controller.show_settings()


if parsed.version:
    print(core.versionstr)

elif parsed.address is not None:

    if parsed.showliveplot:
        root = Tk()
        p = plot.Animate(root,
                         core.Core(parsed.address, parsed.path, parsed.name,
                                   parsed.nofile, not parsed.quiet,
                                   timeout=parsed.timeout),
                         table_length=parsed.tablelength
                         )

        p.grid(row=1, column=0)

        ani = animation.FuncAnimation(p.fig, p.animate,
                                      interval=parsed.refreshfrequency)

        button = Button(root, text='Quit', command=_quit)
        button.grid(row=0, columnspan=2)

        root.mainloop()
        quit()

    elif parsed.cli:
        c = core.Core(parsed.address, parsed.path, parsed.name,
                      parsed.nofile, not parsed.quiet, timeout=parsed.timeout)

        for return_data in c.ping_generator:
            if not c.nofile:
                core.write_csv_data(c.cwriter, return_data)

            time.sleep(parsed.delay)

        quit()

elif parsed.plotfile is not None:
    pf = plot.PlotFile(parsed.plotfile, image_path=parsed.generateimage)
    pf.show_plot()
    quit()

if __name__ == '__main__':
    root = Main()
    root.mainloop()

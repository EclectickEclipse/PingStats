import datetime as dt
import csv
from warnings import warn
import os

from tkinter import *
from tkinter import ttk

from log import plot_logger

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    # import matplotlib.animation as animation
    from matplotlib import style
    import matplotlib.pyplot as plt
except OSError as e:
    raise RuntimeError('Could not load matplotlib!')


class _PlotTable:
        """ A class to maintain a specified number of objects to plot to
        matplotlib.

        Manages two lists:
            self.x (takes `datetime.datetime` objects)
            self.y (takes any `float` data type)
        """

        def __init__(self, length=None):
            """ Creates `self.x` and `self.y`, and validates a table `length`.

            Length must be `int` or None. """

            self.x = []
            self.y = []

            if length is not None and type(length) is not int:
                raise TypeError('length must be int or None')

            if length is None:
                self.length = 250
            elif length <= 0:
                raise ValueError('Requires a table length of at least 1')
            else:
                self.length = int(length)

        def appendx(self, a):
            """ Append a new value to the x value of the table. Maintains
            specified length of table upon reaching max.

            "a" - A `datetime.datetime` object.
            """

            if type(a) is not dt.datetime:
                raise TypeError('Requires a datetime.datetime object')

            if len(self.x) < self.length:
                self.x.append(a)
            else:
                self.x.pop(0)
                self.x.append(a)

        def appendy(self, a):
            """ Append a new value to the y value of the table. Maintains
            specified length of table upon reaching max.

            "a" - Any float.
            """

            if type(a) is not float:
                raise TypeError('PlotTable.appendy requires float type data.')

            if len(self.y) < self.length:
                self.y.append(a)
            else:
                self.y.pop(0)
                self.y.append(a)

        def getx(self):  # arbitrary get method
            return self.x

        def gety(self):  # arbitrary get method
            return self.y


class _Plot(ttk.Frame):
    """ Base class for `Animate` and `PlotFile`, maintains several matplotlib
    properties. """

    fig = Figure(figsize=(5, 5), dpi=100)

    title_str = ''
    for arg in sys.argv:
        if sys.argv.index(arg) is 0:
            pass
        else:
            title_str += ' ' + arg

    ax1 = fig.add_subplot(111)
    fig.subplots_adjust(left=0.13, bottom=0.33, right=0.95, top=0.89)

    @property
    def x_list(self):
        return self.ptable.getx()

    @x_list.setter
    def x_list(self, i):
        self.ptable.appendx(i)

    @property
    def y_list(self):
        return self.ptable.gety()

    @y_list.setter
    def y_list(self, i):
        self.ptable.appendy(i)

    def __init__(self, root, *args, **kwargs):
        """ Validates `self.title_str` and rotates plot labels. """
        super(_Plot, self).__init__(root)
        self.ptable = _PlotTable()

        # table_length validation
        try:
            table_length = kwargs['table_length']
        except KeyError:
            table_length = None
        if table_length is not None and type(table_length) is not int:
            raise TypeError('table_length is not None or int')
        if table_length is not None:
            self.ptable.length = table_length

        # title_str validation
        if type(self.title_str) is not str:
            raise TypeError('Plot title_str requires a string object')
        if self.title_str.count('\x00'):
            raise(ValueError('Title String must not have null bytes'))

        style.use('seaborn-darkgrid')

        for label in self.ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

    def get_figure(self):
        """ Executes `matplotlib.pyplot.show` """
        return self.canvas


class Animate(_Plot):
    """ Handles live plot generation. """
    def animate(self, i):
        """ Calls the next iteration of `c.Core.ping_generator`, and yields
        data to the plot.

        "i" - Required by matplotlib.animation.FuncAnimation
        Returns None.
        """
        self.ax1.clear()

        # TODO Re-enable plot labels
        # self.ax1.xlabel('Timestamps')
        # self.ax1.ylabel('Return Time (in milliseconds)')
        # self.ax1.title('Ping Over Time')

        # DRAW POINTS
        self.ax1.plot_date(self.x_list, self.y_list, 'g-')
        for label in self.ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        self.fig.subplots_adjust(left=0.13, bottom=0.33, right=0.95, top=0.89)

        next(self.get_pings(self.generator))

    def get_pings(self, obj):
        """ Checks for None or appends to `self._PlotTable` """
        for val in obj:
            if not self.nofile:
                plot_logger.debug(val)
                self.core.write_csv(val)

            if val is None:
                yield
            else:
                self.x_list = dt.datetime.fromtimestamp(val[0])

                if val[1] is None:
                    self.y_list = -100.0
                else:
                    self.y_list = val[1]

                yield

    def __init__(self, root, core, *args, **kwargs):
        """ Validates kwargs, and generates a _PlotTable object. """
        super(Animate, self).__init__(root, *args, **kwargs)
        self.core = core
        self.nofile = core.nofile
        if not self.nofile:
            plot_logger.info('write log')
        else:
            plot_logger.info('-sNF')
        self.generator = core.ping_generator


class PlotFile:
    fig = plt.figure(figsize=(5, 5), dpi=100)
    ax1 = plt.axes()

    @staticmethod
    def generate_reader(csv_path):
        """ Yields a `csv.reader` object built from `csv_path`. """
        if not os.access(csv_path, os.F_OK):
            raise RuntimeError('Cannot access %s!' % csv_path)

        return csv.reader(open(csv_path))

    @staticmethod
    def generate_datetime(timestamp):
        """ Yields a `datetime.datetime` object. """
        warn('generate_datetime is deprecated in V2.4', DeprecationWarning)
        if type(timestamp) is not float:
            raise TypeError('timestamp must be float')

        return dt.datetime.fromtimestamp(timestamp)

    def yield_points(self):
        """ Yields an x and y coordinate for each row in `reader` """
        for row in self.creader:
            x = dt.datetime.fromtimestamp(float(row[0]))

            if row[1] == '':  # none
                y = -100.0

            else:
                y = float(row[1])

            yield x, y

    def __init__(self, csv_file, image_path=None):
        # TODO Re-enable plotfile
        plt.subplots_adjust(left=0.13, bottom=0.33, right=0.95, top=0.89)
        style.use('seaborn-darkgrid')
        for label in self.ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        self.image_path = image_path

        self.creader = self.generate_reader(csv_file)

        self.points_generator = self.yield_points()

        self.x = []
        self.y = []

        for a, b in self.points_generator:
            self.x.append(a)
            self.y.append(b)

        self.ax1.plot_date(self.x, self.y, 'r-')

        plt.xlabel('Timestamps')
        plt.ylabel('Return Time (in milliseconds)')
        plt.title('Ping Over Time')

    def show_plot(self):
        if self.image_path is not None:
            plt.savefig(self.image_path)
        else:
            plt.show()

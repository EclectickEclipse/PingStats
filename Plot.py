import sys
from datetime import datetime as dt
import csv

import PingStats as ping

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib import style
except OSError as e:
    raise RuntimeError('Could not load matplotlib!').with_traceback()


class _PlotTable:
        """ A class to maintain a specified number of objects to plot to
        matplotlib. """

        def __init__(self, length=None):
            self.x = []
            self.y = []

            if length is None:
                self.length = 50
            else:
                self.length = int(length)

        def appendx(self, a):
            """ Append a new value to the x value of the table. Maintains
            specified length of table upon reaching max.

            "a" - The value to append to the table.
            """
            if len(self.x) < self.length:
                self.x.append(a)
            else:
                self.x.pop(0)
                self.x.append(a)

        def appendy(self, a):
            """ Append a new value to the y value of the table. Maintains
            specified length of table upon reaching max.

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


class Plot:
    fig = plt.figure()

    title_str = ''
    for arg in sys.argv:
        if sys.argv.index(arg) is 0:
            pass
        else:
            title_str += ' ' + arg

    ax1 = fig.add_subplot(1, 1, 1)

    ptable = _PlotTable

    nofile = False

    def __init__(self, csv_file, **kwargs):

        self.fig.canvas.set_window_title('%s | %s' % (ping.buildname,
                                                      self.title_str))
        if csv_file is None:
            raise RuntimeError('Plot object requires a csv_file!')
        else:
            self.csv_file = csv_file

        style.use('fivethirtyeight')

        plt.subplots_adjust(left=0.13, bottom=0.33, right=0.95, top=0.89)
        for label in self.ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

    def show_plot(self):
        try:
            plt.show()
            return True
        except BaseException:
            return False


class Animate(Plot):
    def __init__(self, parser=None, nofile=False, verbose=True,
                 table_length=None, refresh_freq=None, **kwargs):
        super(Animate, self).__init__(**kwargs)

        self.nofile = nofile
        self.verbose = verbose
        if table_length is not None:
            self.ptable(table_length)
        else:
            self.ptable()

        self.parser = parser

        if refresh_freq is None:
            self.ani = animation.FuncAnimation(self.fig, self._animate,
                                               interval=500)
        else:
            self.ani = animation.FuncAnimation(self.fig, self._animate,
                                               interval=refresh_freq)

    def _animate(self, i):
        """ Reads rows from a CSV file and render them to a plot.

        "i" - Required by matplotlib.animation.FuncAnimation
        Returns None.
        """

        # GET DATA
        data_generator = self.parser
        if data_generator is not None:
            for newrow in data_generator:  # some code linter's may read this
                # as NoneType, this is handled...
                if not self.no_file:
                    ping.write_csv_data(self.csv_file, newrow, self.verbose)
                elif self.verbose:
                    print(newrow)
                self.ptable.appendx(dt.datetime.fromtimestamp(float(
                    newrow[0])))
                self.ptable.appendy(newrow[5].split('=')[1])

        # DRAW POINTS
        self.ax1.clear()
        self.ax1.plot_date(self.ptable.getx(), self.ptable.gety(), '-',
                           label='Connection over time')
        self.ax1.plot(self.ptable.getx(), self.ptable.gety())
        for label in self.ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        plt.xlabel('Timestamps')
        plt.ylabel('Return Time (in milliseconds)')
        plt.title('Ping Over Time')

    def animate(self):
        self.ani.new_frame_seq()
        return self.show_plot()


class PlotFile(Plot):
    table = []

    def __init__(self):
        super(PlotFile, self).__init__()

        with open(self.csv_file) as cf:
            creader = csv.reader(cf)
            for line in creader:
                self.table.append(line)

        self.x = []
        self.y = []

        for i, newrow in enumerate(self.table):
            try:
                self.x.append(dt.fromtimestamp(float(newrow[0])))
                self.y.append(newrow[5].split('=')[1])
            except IndexError as e:
                print('Could not read line #%s %s, python through %s' % (
                    i + 1, newrow, e))

        self.ax1.plot(self.x, self.y)

        plt.xlabel('Timestamps')
        plt.ylabel('Return Time (in milliseconds)')
        plt.title('Ping Over Time')

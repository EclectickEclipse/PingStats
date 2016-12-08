import sys
import csv
import threading
import datetime as dt

import core as c


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

            if length is not None and type(length) is not int:
                raise TypeError('length must be int or None')

            if length is None:
                self.length = 250
            elif length == 0:
                raise ValueError('Requires a table length of at least 1')
            else:
                self.length = int(length)

        def appendx(self, a):
            """ Append a new value to the x value of the table. Maintains
            specified length of table upon reaching max.

            "a" - The value to append to the table.
            """

            if type(a) is not dt.datetime:
                raise TypeError('Requires a datetime.datetime.fromtimestamp '
                                'object')

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


class _Plot:
    fig = plt.figure()

    title_str = ''
    for arg in sys.argv:
        if sys.argv.index(arg) is 0:
            pass
        else:
            title_str += ' ' + arg

    ax1 = plt.axes()

    ptable = _PlotTable()

    nofile = False

    def __init__(self):
        if type(self.title_str) is not str:
            raise TypeError('Plot title_str requires a string object')

        if self.title_str.count('\x00'):
            raise(ValueError('Title String must not have null bytes'))

        self.fig.canvas.set_window_title('%s | %s' % (c.buildname,
                                                      self.title_str))
        # style.use('ggplot')
        style.use('seaborn-darkgrid')

        plt.subplots_adjust(left=0.13, bottom=0.33, right=0.95, top=0.89)
        for label in self.ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

    def show_plot(self):
        # plt.show(block=False)
        return plt.show()


class Animate(_Plot):
    def _animate(self, i, ptable):
        """ Reads rows from a CSV file and render them to a plot.

        "i" - Required by matplotlib.animation.FuncAnimation
        Returns None.
        """
        self.ax1.clear()

        plt.xlabel('Timestamps')
        plt.ylabel('Return Time (in milliseconds)')
        plt.title('Ping Over Time')

        # DRAW POINTS
        self.ax1.plot_date(ptable.getx(), ptable.gety(), 'r-')
        for label in self.ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

    def animate(self):
        self.t.start()
        return self.show_plot()

    def close_thread(self, *args):
        self.t.join()
        if self.t.isAlive():
            raise RuntimeError('Could not join ping thread').with_traceback()
        exit()
        plt.close('all')

    def get_pings(self, obj):
        for val in obj:
            self.ptable.appendx(val[0])

            if val[1] is None:
                self.ptable.appendy(-100.0)
            else:
                self.ptable.appendy(val[1])

    def __init__(self, ping_obj, table_length=None, refresh_freq=None):
        super(Animate, self).__init__()

        if table_length is not None:
            self.ptable.length = table_length

        if refresh_freq is None:
            self.ani = animation.FuncAnimation(self.fig, self._animate,
                                               fargs=(
                                                   self.ptable,))
        else:
            self.ani = animation.FuncAnimation(self.fig, self._animate,
                                               interval=refresh_freq, fargs=(
                                                    self.ptable,))

        self.fig.canvas.mpl_connect('close_event', self.close_thread)

        self.t = threading.Thread(target=self.get_pings, args=(ping_obj,))

    def __del__(self, *args):
        self.t.join()


class PlotFile(_Plot):  # TODO Fix static plot generation
    table = []

    def __init__(self, csv_file):
        super(PlotFile, self).__init__()

        with open(csv_file) as cf:
            creader = csv.reader(cf)

            x, y = [], []

            for row in creader:
                x.append(row[0])
                if row[1] is None:
                    y.append(-100)
                else:
                    y.append(row[1])

        self.ax1.plot_date(x, y)  # TODO `ax1.plot_date` wont accept dates

        plt.xlabel('Timestamps')
        plt.ylabel('Return Time (in milliseconds)')
        plt.title('Ping Over Time')

        plt.show()

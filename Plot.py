import sys
from datetime import datetime as dt
import csv
from threading import Thread

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

    ptable = _PlotTable()

    nofile = False

    def __init__(self):

        self.fig.canvas.set_window_title('%s | %s' % (ping.buildname,
                                                      self.title_str))
        style.use('fivethirtyeight')

        plt.subplots_adjust(left=0.13, bottom=0.33, right=0.95, top=0.89)
        for label in self.ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

    def show_plot(self):
        try:
            plt.show(block=False)
            return True
        except BaseException:
            return False


class Animate(Plot):
    def __init__(self, table_length=None, refresh_freq=None):
        super(Animate, self).__init__()

        if table_length is not None:
            self.ptable.length = table_length

        if refresh_freq is None:
            self.ani = animation.FuncAnimation(self.fig, self._animate,
                                               interval=60)
        else:
            self.ani = animation.FuncAnimation(self.fig, self._animate,
                                               interval=refresh_freq)

    def _animate(self, i):
        """ Reads rows from a CSV file and render them to a plot.

        "i" - Required by matplotlib.animation.FuncAnimation
        Returns None.
        """

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
        plt.draw()

    def animate(self):
        self.ani.new_frame_seq()
        return self.show_plot()

class PlotFile(Plot):
    table = []

    def __init__(self, csv_file):
        super(PlotFile, self).__init__()

        with open(csv_file) as cf:
            creader = csv.reader(cf)
            for line in creader:
                self.table.append(line)

        self.x = []
        self.y = []

        for i, newrow in enumerate(self.table):
            try:
                self.x.append(str(newrow[0]))
                if newrow[1] is not None:
                    self.y.append(str(newrow[1]))
                else:
                    self.y.append(str(-10))
            except IndexError as e:
                print('Could not read line #%s %s, python through %s' % (
                    i + 1, newrow, e))

        self.ax1.plot(self.x, self.y)

        plt.xlabel('Timestamps')
        plt.ylabel('Return Time (in milliseconds)')
        plt.title('Ping Over Time')

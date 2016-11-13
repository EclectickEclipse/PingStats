import sys
import csv
import threading

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
                self.length = 250
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

        self.fig.canvas.set_window_title('%s | %s' % (ping.buildname,
                                                      self.title_str))
        style.use('ggplot')

        plt.subplots_adjust(left=0.13, bottom=0.33, right=0.95, top=0.89)
        for label in self.ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

    def show_plot(self):
        # plt.show(block=False)
        plt.show()


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
        exit()

    def get_pings(self, obj):
        for val in obj:
            self.ptable.appendx(val[0])
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

        # self.ani.new_frame_seq()
        self.t = threading.Thread(target=self.get_pings, args=(ping_obj,))

    def __del__(self, *args):
        self.t.join()


class PlotFile(_Plot):
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


def run_test():
    Animate(ping.ping('google.ca'), 250).animate()
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        exit()

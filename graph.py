import matplotlib
from kivy.clock import Clock

from kivy.uix.boxlayout import BoxLayout

import matplotlib.pyplot as plt
from matplotlib import style

from resources.plot_table import PlotTable
matplotlib.use('module://resources.backend_kivy')  # I HATE THIS!
# Can we assign the matplotlib backend to backend_kivy.py elsewhere?

if __name__ == '__main__':
    from kivy.app import App
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label


class PingGraph(BoxLayout):
    def __init__(self, **kwargs):
        self.orientation = "vertical"
        super(PingGraph, self).__init__(**kwargs)

        # Create a figure
        fig, ax = plt.subplots()
        style.use('seaborn-dark-palette')
        for label in ax.xaxis.get_ticklabels():
            label.set_rotation(45)
        self.ax = ax
        plt.xlabel('Sequence Number')
        plt.ylabel('Return Time')
        plt.plot(self._table.x, self._table.y)
        self.py_plot = plt

        # Get Canvas
        canvas = fig.canvas
        self.fig_canvas = canvas
        self.add_widget(canvas)

    def trigger_draw(self, *args):
        """ Triggers `self.fig_canvas.draw()`. """
        self.ax.clear()
        try:
            self.py_plot.plot(self._table.x, self._table.y)
        except:
            pass
        self.fig_canvas.draw()


if __name__ == '__main__':
    class TestGraphApp(App):
        graph = PingGraph()

        table_length = str((len(graph._table.x), len(graph._table.y)))

        announce_label = Label(text=table_length, size_hint_y=0.2)

        pos = 0

        def give_point(self, *args):
            self.graph.update_points(None, (self.pos, self.pos))
            self.pos += 1

        def announce_length(self, instance, *args):
            self.table_length = str((len(self.graph._table.x),
                                     len(self.graph._table.y)))
            self.announce_label.text = self.table_length

        def __init__(self, **kwargs):
            super(TestGraphApp, self).__init__(**kwargs)
            Clock.schedule_interval(self.give_point, 1/2)

        def build(self):
            layout = GridLayout(cols=1)
            layout.add_widget(self.announce_label)
            layout.add_widget(self.graph)
            return layout

    TestGraphApp().run()

# Kivy runtime
from kivy.app import App

# Kivy UI
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.switch import Switch

# Core
import plot

settings = {  # GLOBAL SETTINGS DATA
    'address': 'google.ca',
    'track': {
        'return': True,
        'ttl': False
    },

    'csv': {
        'name': 'PingStatsLog',
        'path': './',
        'generate': True
    },

    'core': {
        'wait': 0.22,
        'length': 250
    }
}


class MainSettings(GridLayout):
    # TODO size address input properly
    # TODO validate address input text
    cols = 1

    spacing = [50, 50]

    def report_address(self, isntance, value):
        global settings
        settings['address'] = value

    def __init__(self, **kwargs):
        super(MainSettings, self).__init__(**kwargs)
        # Address
        self.address_box = GridLayout(cols=2)
        address_label = Label(text='Address:')
        address_input = TextInput(text='google.ca', multiline=False,
                                  size_hint_y=0.3)
        address_input.bind(on_text_validate=self.report_address)

        self.address_box.add_widget(address_label)
        self.address_box.add_widget(address_input)
        self.add_widget(self.address_box)

        self.add_widget(MainModeSelect())


class MainModeSelect(GridLayout):
    rows = 2

    spacing = [50, 50]

    def report_return_time(self, instance, value):
        global settings
        settings['track']['return'] = value

    def report_ttl(self, instance, value):
        global settings
        settings['track']['ttl'] = value

    def __init__(self, **kwargs):
        super(MainModeSelect, self).__init__(**kwargs)

        # return time
        self.add_widget(Label(text='Track return time:'))
        self.return_time = Switch(active=True)
        self.return_time.bind(active=self.report_return_time)
        self.add_widget(self.return_time)

        # average ttl
        self.add_widget(Label(text='Track TTL (under construction):'))
        self.ttl = Switch(active=False)
        self.add_widget(self.ttl)


class AdvancedSettings(GridLayout):
    # TODO validate csv_name text
    # TODO validate csv_path text
    # TODO track file generation
    # TODO validate core_wait text
    # TODO validate core_length text
    cols = 2

    spacing = [50, 50]

    def report_csv_name(self, instance, value):
        global settings
        settings['csv']['name'] = value

    def report_csv_path(self, instance, value):
        global settings
        settings['csv']['path'] = value

    def report_generate_file(self, instance, value):
        global settings
        settings['csv']['generate'] = value

    def report_core_wait(self, instance, value):
        global settings
        settings['core']['wait'] = float(value)

    def report_core_length(self, instance, value):
        global settings
        settings['core']['length'] = float(value)

    def __init__(self, **kwargs):
        super(AdvancedSettings, self).__init__(**kwargs)

        # Custom PingStatsLog.csv output name
        self.add_widget(Label(text='CSV output name:'))
        self.csv_name = TextInput(text='PingStatsLog.csv', multiline=False)
        self.csv_name.bind(on_text_validate=self.report_csv_name)
        self.add_widget(self.csv_name)

        # Custom PingStatsLog.csv output path
        self.add_widget(Label(text='CSV output path:'))
        self.csv_path = TextInput(text='./', multiline=False)
        self.csv_path.bind(on_text_validate=self.report_csv_path)
        self.add_widget(self.csv_path)

        # Omit csv file generation
        self.add_widget(Label(text='CSV Log generation:', size_hint_y=0.3))
        self.generate_file = Switch(active=True, size_hint_y=0.3)
        self.generate_file.bind(active=self.report_generate_file)
        self.add_widget(self.generate_file)

        # Time Between Pings
        self.add_widget(Label(text='Time to wait between ping requests'))
        self.core_wait = TextInput(text='0.22', multiline=False)
        self.core_wait.bind(on_text_validate=self.report_core_wait)
        self.add_widget(self.core_wait)

        # PlotTable length
        self.add_widget(Label(text='Number of results to show on screen'))
        self.core_length = TextInput(text='250')
        self.core_length.bind(on_text_validate=self.report_core_length)
        self.add_widget(self.core_length)


class PaneSelect(Accordion):
    def __init__(self, **kwargs):
        super(PaneSelect, self).__init__(**kwargs)
        # LANDING PAGE
        self.main_settings_pane = AccordionItem(title='Main Settings')
        self.main_settings = MainSettings()
        self.main_settings_pane.add_widget(self.main_settings)

        # ADVANCED SETTINGS PANE
        self.advanced_settings_pane = AccordionItem(title='Advanced Settings')
        self.advanced_settings = AdvancedSettings()
        self.advanced_settings_pane.add_widget(self.advanced_settings)

        self.add_widget(self.main_settings_pane)
        self.add_widget(self.advanced_settings_pane)

        self.select(self.main_settings_pane)


class PlotScreen(Screen):
    # TODO Actually implement graph
    def render_graph(self):
        global settings

        self.plot = plot.Animate(
            address=settings['address'],
            file_path=settings['csv']['path'],
            file_name=settings['csv']['name'],
            nofile=settings['csv']['generate'],
            delay=settings['core']['wait'],
            table_length=settings['core']['length']
        )

        self.layout.add_widget(plot, index=0)

    def remove_graph(self):
        self.remove_widget(plot)
        self.plot = None

    def __init__(self, **kwargs):
        super(PlotScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.button = Button(text='Stop')
        self.layout.add_widget(self.button)
        self.add_widget(self.layout)


class SettingsScreen(Screen):
    # TODO Gather settings when go is pressed

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        layout.add_widget(PaneSelect())

        self.go = Button(text='Go', size_hint_y=0.2)

        layout.add_widget(self.go)

        self.add_widget(layout)


class Root(ScreenManager):
    transition = FadeTransition()

    def show_plot(self, instance):
        self.current = 'graph'
        self.graph.render_graph()

    def show_settings(self, instance):
        self.current = 'settings'
        self.graph.remove_graph()

    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        self.settings = SettingsScreen(name='settings')
        self.graph = PlotScreen(name='graph')

        self.settings.go.bind(on_press=self.show_plot)
        self.graph.button.bind(on_press=self.show_settings)

        self.add_widget(self.settings)
        self.add_widget(self.graph)
        self.current = 'settings'


if __name__ == '__main__':
    class App(App):
        def build(self):
            return Root()

    App().run()

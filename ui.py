# Kivy runtime
from kivy.app import App

# Kivy UI
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.switch import Switch


class MainSettings(GridLayout):
    # TODO size address input properly
    # TODO validate address input text
    cols = 1

    spacing = [50, 50]

    def __init__(self, **kwargs):
        super(MainSettings, self).__init__(**kwargs)
        # Address
        self.address_box = GridLayout(cols=2)
        address_label = Label(text='Address:')
        address_input = TextInput(text='google.ca', multiline=False,
                                  size_hint_y=0.3)
        self.address_box.add_widget(address_label)
        self.address_box.add_widget(address_input)
        self.add_widget(self.address_box)

        self.add_widget(MainModeSelect())


class MainModeSelect(GridLayout):
    # TODO track state of switches
    rows = 2

    spacing = [50, 50]

    def __init__(self, **kwargs):
        super(MainModeSelect, self).__init__(**kwargs)

        # return time
        self.add_widget(Label(text='Track return time:'))
        self.return_time = Switch(active=True)
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

    def __init__(self, **kwargs):
        super(AdvancedSettings, self).__init__(**kwargs)

        # Custom PingStatsLog.csv output name
        self.add_widget(Label(text='CSV output name:'))
        self.csv_name = TextInput(text='PingStatsLog.csv', multiline=False)
        self.add_widget(self.csv_name)

        # Custom PingStatsLog.csv output path
        self.add_widget(Label(text='CSV output path:'))
        self.csv_path = TextInput(text='./', multiline=False)
        self.add_widget(self.csv_path)

        # Omit csv file generation
        self.add_widget(Label(text='CSV Log generation:', size_hint_y=0.3))
        self.generate_file = Switch(active=True, size_hint_y=0.3)
        self.add_widget(self.generate_file)

        # Time Between Pings
        self.add_widget(Label(text='Time to wait between ping requests'))
        self.core_wait = TextInput(text='0.22', multiline=False)
        self.add_widget(self.core_wait)

        # PlotTable length
        self.add_widget(Label(text='Number of results to show on screen'))
        self.core_length = TextInput(text='250')
        self.add_widget(self.core_length)


class GraphDisplay(Widget):
    # TODO Display graph

    def __init__(self, **kwargs):
        super(GraphDisplay, self).__init__(**kwargs)


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


class Root(BoxLayout):
    # TODO Gather settings when go is pressed
    # TODO Switch to graph screen when go is pressed
    orientation = 'vertical'

    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)

        self.add_widget(PaneSelect())

        self.go = Button(text='Go', size_hint_y=0.2)

        self.add_widget(self.go)


if __name__ == '__main__':
    class App(App):
        def build(self):
            return Root()

    App().run()

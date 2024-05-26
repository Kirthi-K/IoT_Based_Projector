import requests
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

#192.168.43.215
# GLOBALS
SERVER_URL = None

class ServerURLScreen(Screen):
    def __init__(self, **kwargs):
        super(ServerURLScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.url_input = TextInput(hint_text='Enter server URL', multiline=False)
        submit_button = Button(text='Submit', size_hint=(None, None), size=(150, 50))
        submit_button.bind(on_press=self.submit_url)
        layout.add_widget(self.url_input)
        layout.add_widget(submit_button)
        self.add_widget(layout)

    def submit_url(self, instance):
        global SERVER_URL
        SERVER_URL = self.url_input.text
        # Ensure the URL starts with 'http://'
        if not SERVER_URL.startswith('http://'):
            SERVER_URL = 'http://' + SERVER_URL + ':5000'
        print(f"Server URL updated to: {SERVER_URL}")
        # Switch to the next screen after successful update
        self.manager.current = 'connect'


class ConnectScreen(Screen):
    def __init__(self, **kwargs):
        super(ConnectScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        connect_button = Button(text='Connect to Projector', size_hint=(None, None), size=(150, 50))
        connect_button.bind(on_press=self.switch_to_file_select)
        layout.add_widget(connect_button)
        self.add_widget(layout)

    def switch_to_file_select(self, instance):
        self.manager.current = 'file_select'

class FileSelectScreen(Screen):
    def __init__(self, **kwargs):
        super(FileSelectScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.file_chooser = FileChooserListView()
        layout.add_widget(self.file_chooser)
        select_button = Button(text='Select File', size_hint=(None, None), size=(150, 50))
        select_button.bind(on_press=self.select_file)
        layout.add_widget(select_button)
        self.add_widget(layout)

    def select_file(self, instance):
        selected_file = self.file_chooser.selection and self.file_chooser.selection[0]
        if selected_file:
            self.upload_file(selected_file)

    def upload_file(self, file_path):
        files = {'file': open(file_path, 'rb')}
        response = requests.post(f'{SERVER_URL}/upload', files=files)
        if response.status_code == 200:
            print("File uploaded successfully.")
            # Switch to navigation screen after successful upload
            self.manager.get_screen('navigation').load_file(file_path)
            self.manager.current = 'navigation'
        else:
            print(f"Error uploading file: {response.text}")

class NavigationScreen(Screen):
    def __init__(self, **kwargs):
        super(NavigationScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.image = Image()
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.6))
        self.scroll_view.add_widget(self.image)
        layout.add_widget(self.scroll_view)
        nav_layout = BoxLayout(size_hint=(1, None), height=50)
        prev_button = Button(text='Previous', size_hint=(None, None), size=(150, 50))
        prev_button.bind(on_press=self.prev_page)
        next_button = Button(text='Next', size_hint=(None, None), size=(150, 50))
        next_button.bind(on_press=self.next_page)
        close_button = Button(text='Close Presentation', size_hint=(None, None), size=(150, 50))
        close_button.bind(on_press=self.switch_to_connect)
        nav_layout.add_widget(prev_button)
        nav_layout.add_widget(next_button)
        nav_layout.add_widget(close_button)
        layout.add_widget(nav_layout)
        self.add_widget(layout)
        self.file_path = None

    def load_file(self, file_path):
        self.file_path = file_path
        self.image.source = file_path

    def prev_page(self, instance):
        if self.file_path:
            self.navigate_file('previous')

    def next_page(self, instance):
        if self.file_path:
            self.navigate_file('next')

    def switch_to_connect(self, instance):
        self.manager.current = 'connect'

    def navigate_file(self, direction):
        data = {'filename': self.file_path.split('/')[-1], 'direction': direction}
        response = requests.post(f'{SERVER_URL}/navigate', json=data)
        if response.status_code == 200:
            new_file = response.json().get('message')
            if new_file:
                self.load_file(new_file)
                print(f"File navigated {direction} successfully.")
            else:
                print("Failed to navigate file.")
        else:
            print(f"Error navigating file: {response.text}")

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ServerURLScreen(name='server_url'))
        sm.add_widget(ConnectScreen(name='connect'))
        sm.add_widget(FileSelectScreen(name='file_select'))
        sm.add_widget(NavigationScreen(name='navigation'))
        sm.current = 'server_url'
        # Set minimum and maximum window size
        Window.min_width, Window.min_height = 320, 480
        Window.max_width, Window.max_height = 1024, 768
        return sm

if __name__ == '__main__':
    MyApp().run()


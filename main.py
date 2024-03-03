from kivy.metrics import dp
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton
from kivy.uix.screenmanager import ScreenManager, NoTransition

import backend
from plyer import filechooser

import pandas as pd
import multiprocessing

import os
import encoding

import shutil



class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        self.username_input = Builder.load_string("""
MDTextField:
    hint_text: "Enter username"
    helper_text: "admin"
    helper_text_mode: "on_focus"
    icon_right: "android"
    icon_right_color: app.theme_cls.primary_color
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    size_hint_x: None
    width: 300
        """)

        self.password_input = Builder.load_string("""
MDTextField:
    hint_text: "Enter password"
    helper_text: "dei2020"
    helper_text_mode: "on_focus"
    password: True
    icon_right: "lock"
    icon_right_color: app.theme_cls.primary_color
    pos_hint: {'center_x': 0.5, 'center_y': 0.4}
    size_hint_x: None
    width: 300
        """)

        button = MDRectangleFlatButton(text='Login',
                                       pos_hint={'center_x': 0.5, 'center_y': 0.3},
                                       on_release=self.login)

        self.add_widget(self.username_input)
        self.add_widget(self.password_input)
        self.add_widget(button)

    def login(self, obj):
        app = MDApp.get_running_app()
        if self.username_input.text == "admin" and self.password_input.text == "dei2020":
            app.root.current = 'dashboard'


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)

        button_mark_attendance = MDRectangleFlatButton(text='Mark Attendance',
                                                       pos_hint={'center_x': 0.5, 'center_y': 0.6},
                                                       on_release=self.go_to_mark_attendance)

        button_database = MDRectangleFlatButton(text='Database',
                                                pos_hint={'center_x': 0.5, 'center_y': 0.4},
                                                on_release=self.go_to_database)
        button_class=MDRectangleFlatButton(text='Add student / class',
                                                pos_hint={'center_x': 0.5, 'center_y': 0.2},
                                                on_release=self.go_to_class)

        self.add_widget(button_mark_attendance)
        self.add_widget(button_database)
        self.add_widget(button_class)

    def go_to_mark_attendance(self, obj):
        app = MDApp.get_running_app()
        app.root.current = 'screen1'

    def go_to_database(self, obj):
        app = MDApp.get_running_app()
        app.root.current = 'screen2'
    
    def go_to_class(self,obj):
        app=MDApp.get_running_app()
        app.root.current='screen3'


class Screen1(Screen):
    def __init__(self, **kwargs):
        super(Screen1, self).__init__(**kwargs)

        self.username_input = Builder.load_string("""
MDTextField:
    hint_text: "Enter class name"
    helper_text: "or click on forgot username"
    helper_text_mode: "on_focus"
    icon_right: "android"
    icon_right_color: app.theme_cls.primary_color
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    size_hint_x: None
    width: 300
        """)

        self.file_path_input = Builder.load_string("""
MDFloatLayout:
    MDRaisedButton:
        text: "Upload"
        pos_hint: {"center_x": 0.5, "center_y": 0.4}
        on_release: app.root.get_screen('screen1').file_chooser()
        """)

        back_button = MDRaisedButton(text='Back to Dashboard',
                                     pos_hint={'center_x': 0.5, 'center_y': 0.2},
                                     on_release=self.go_to_dashboard)

        button = MDRectangleFlatButton(text='Submit',
                                       pos_hint={'center_x': 0.5, 'center_y': 0.3},
                                       on_release=self.show_data)

        self.add_widget(self.username_input)
        self.add_widget(button)
        self.add_widget(self.file_path_input)
        self.add_widget(back_button)

    def file_chooser(self):
        filechooser.open_file(on_selection=self.selected)

    def selected(self, selection):
        app = MDApp.get_running_app()
        app.filePath = selection[0]
        print(selection[0])

    def show_data(self, obj):
        app = MDApp.get_running_app()
        app.class_name = self.username_input.text
        print(app.filePath, app.class_name)
        backend_process = multiprocessing.Process(target=run_backend, args=(app.class_name, app.filePath))
        backend_process.start()
        # with ProcessPoolExecutor() as executor:
        #     # Using partial to pass multiple arguments to the threaded_func
        #     func = partial(self.threaded_func, app.filePath, app.class_name)
        #     future = executor.submit(func)

        # # Attach a callback to the future to switch to the next screen after completion
        # future.add_done_callback(lambda x: self.switch_to_screen2())

        print("Processing in the background...")
        # app.root.current = 'screen2'
    

    
    def threaded_func(self,filePath,class_name):
        backend.process_attendance(filePath, class_name)
    
    
    def switch_to_screen2(self):
        app = MDApp.get_running_app()
        app.root.current = 'screen2'


    def go_to_dashboard(self, obj):
        app = MDApp.get_running_app()
        app.root.current = 'dashboard'


class Screen2(Screen):

    def __init__(self, **kwargs):
        super(Screen2, self).__init__(**kwargs)

        self.class_name_input = Builder.load_string("""
MDTextField:
    hint_text: "Enter class name"
    helper_text: "or click on forgot username"
    helper_text_mode: "on_focus"
    icon_right: "android"
    icon_right_color: app.theme_cls.primary_color
    pos_hint: {'center_x': 0.5, 'center_y': 0.9}
    size_hint_x: None
    width: 300
        """)

        button = MDRectangleFlatButton(text='Submit',
                                       pos_hint={'center_x': 0.5, 'center_y': 0.8},
                                       on_release=self.submit_btn)
        DATA = pd.read_excel("Attendance_iot.xlsx")
        DATA = DATA.iloc[:, 0:]
        cols = DATA.columns.values
        values = DATA.values

        self.data_tables = MDDataTable(
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            size_hint=(0.9, 0.6),
            use_pagination=True,
            column_data=[
                (col, dp(30))
                for col in cols
            ],
            row_data=values
        )

        layout = MDFloatLayout()
        layout.add_widget(self.data_tables)
        layout.add_widget(self.class_name_input)
        layout.add_widget(button)
        self.add_widget(layout)

        back_button = MDRaisedButton(text='Back to Dashboard',
                                     pos_hint={'center_x': 0.5, 'center_y': 0.2},
                                     on_release=self.go_to_dashboard)

        self.add_widget(back_button)


    def submit_btn(self, instance):
        app = MDApp.get_running_app()
        class_name1 = self.class_name_input.text
        file_path = os.path.join("database", f"{class_name1}", "Attendance_iot.xlsx")

        try:
            DATA = pd.read_excel(file_path)
            DATA = DATA.iloc[:, 0:]
            cols = DATA.columns.values
            values = DATA.values

            self.data_tables.column_data = [(col, dp(30)) for col in cols]
            self.data_tables.row_data = values

        except FileNotFoundError:
            print(f"File {file_path} not found. Please check the file path.")

    def go_to_dashboard(self, obj):
        app = MDApp.get_running_app()
        app.root.current = 'dashboard'

class Screen3(Screen):
    def __init__(self, **kwargs):
        super(Screen3, self).__init__(**kwargs)

        self.name_input = Builder.load_string("""
MDTextField:
    hint_text: "Enter name"
    helper_text: "optional"
    helper_text_mode: "on_focus"
    icon_right: "android"
    icon_right_color: app.theme_cls.primary_color
    pos_hint: {'center_x': 0.5, 'center_y': 0.7}
    size_hint_x: None
    width: 300
        """)

        self.class_name_input = Builder.load_string("""
MDTextField:
    hint_text: "Enter class name"
    helper_text: "or click on forgot username"
    helper_text_mode: "on_focus"
    icon_right: "android"
    icon_right_color: app.theme_cls.primary_color
    pos_hint: {'center_x': 0.5, 'center_y': 0.6}
    size_hint_x: None
    width: 300
        """)

        self.roll_no_input = Builder.load_string("""
MDTextField:
    hint_text: "Enter roll number"
    helper_text: "optional"
    helper_text_mode: "on_focus"
    icon_right: "android"
    icon_right_color: app.theme_cls.primary_color
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    size_hint_x: None
    width: 300
        """)
        self.file_path_input = Builder.load_string("""
MDFloatLayout:
    MDRaisedButton:
        text: "Upload"
        pos_hint: {"center_x": 0.5, "center_y": 0.4}
        on_release: app.root.get_screen('screen1').file_chooser()
        """)

        back_button = MDRaisedButton(text='Back to Dashboard',
                                     pos_hint={'center_x': 0.5, 'center_y': 0.2},
                                     on_release=self.go_to_dashboard)

        submit_button = MDRectangleFlatButton(text='Submit',
                                              pos_hint={'center_x': 0.5, 'center_y': 0.3},
                                              on_release=self.submit_data)

        self.add_widget(self.name_input)
        self.add_widget(self.class_name_input)
        self.add_widget(self.roll_no_input)
        self.add_widget(self.file_path_input)
        self.add_widget(submit_button)
        self.add_widget(back_button)

    def submit_data(self, obj):
        app = MDApp.get_running_app()
        name = self.name_input.text
        class_name = self.class_name_input.text
        roll_number = self.roll_no_input.text
        filePath1=app.filePath
        print(filePath1)
        create_student_folder(os.path.join("database", class_name))
        copy_and_rename_file(name,roll_number,class_name,filePath1)
        encoding_process = multiprocessing.Process(target=run_encoding, args=(name,roll_number,class_name,filePath1))
        encoding_process.start()
        # Process the data as needed (e.g., save to a file, send to a database)
        print(f"Name: {name}, Class Name: {class_name}, Roll Number: {roll_number}, File Path:{filePath1}")

        # You can add additional logic here to save or process the data as needed.

        # After processing, you can navigate to another screen if needed.
        # app.root.current = 'some_other_screen'

    def file_chooser(self):
        filechooser.open_file(on_selection=self.selected)
    def selected(self, selection):
        app = MDApp.get_running_app()
        app.filePath = selection[0]
        print(selection[0])
    def go_to_dashboard(self, obj):
        app = MDApp.get_running_app()
        app.root.current = 'dashboard'



class DemoApp(MDApp):
    class_name = ''
    filePath = ''

    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(Screen1(name='screen1'))
        sm.add_widget(Screen2(name='screen2'))
        sm.add_widget(Screen3(name='screen3'))

        return sm
def run_backend(class_name, video_path):
    backend.process_attendance(video_path,class_name)

def run_encoding(name,rollno,class_name,file_path):
    encoding.encode_faces_for_class(class_name)
def create_student_folder(class_name):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    print(f"The script is located in: {script_directory}")
    class_directory = os.path.join(script_directory, class_name)
    print(class_directory)

    # Step 1: Create a folder for the class if it doesn't exist
    if not os.path.exists(class_directory):
        os.makedirs(class_directory)

    return class_directory

def copy_and_rename_file(name, roll_no, class_name, file_path):
    # Step 2: Copy the file to the class directory with the specified format
    file_name = f"{name}_{roll_no}_{class_name}.jpg"
    script_directory = os.path.dirname(os.path.abspath(__file__))
    destination_path = f'{script_directory}\\database\\{class_name}\\{file_name}'
    shutil.copyfile(file_path, destination_path)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    DemoApp().run()

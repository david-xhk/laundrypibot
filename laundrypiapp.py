#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.app import App
import laundrypidb
import laundrypibot
import os

os.environ['KIVY_GL_BACKEND'] = 'gl'


class UnicodeButton(Button):
    def __init__(self, **kwargs):
        Button.__init__(self, **kwargs)
        self.font_name = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
        self.font_size = 72


class MyLabel(Label):
    def __init__(self, **kwargs):
        Label.__init__(self, **kwargs)
        self.font_name = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
        self.padding = (70, 20)


class MyTextInput(TextInput):
    def __init__(self, **kwargs):
        TextInput.__init__(self, **kwargs)
        self.font_size = 72
        self.keyboard_mode = "managed"
        self.multiline = False
        self.focus = True
        self.unfocus_on_touch = False
        self.hold_backspace = Clock.create_trigger(lambda dt: self.do_backspace(), interval=True, timeout=0.1)
    
    def press_backspace(self):
        self.do_backspace()
        if not self.hold_backspace.is_triggered:
            self.hold_backspace()
    
    def release_backspace(self):
        if self.hold_backspace.is_triggered:
            self.hold_backspace.cancel()
        

class LaundryPiApp(App):
    def build(self):
        layout = BoxLayout()
        labels = self.build_labels()
        keypad = self.build_keypad()

        layout.add_widget(labels)
        layout.add_widget(keypad)
        
        self.current_state = "waiting for washer id"
        self.chosen_washer_id = None
        self.get_next_state()

        return layout
    
    
    def build_labels(self):
        layout = BoxLayout(orientation="vertical", size_hint=(0.5, 1))
        layout.bind(width=self._update_labels)
        
        self.label1 = MyLabel(size_hint=(1,0.2), font_size=24, halign="center", underline=True)
        self.label2 = MyLabel(size_hint=(1,0.8), font_size=18, halign="left")
        
        layout.add_widget(self.label1)
        layout.add_widget(self.label2)
        
        return layout
    
    
    def build_keypad(self):
        layout = BoxLayout(orientation="vertical", size_hint=(0.5, 1))
        
        self.textinput = MyTextInput(size_hint=(1, 0.2))
        
        btns = GridLayout(rows=4, cols=3)
        for i in range(1,10):
            btns.add_widget(UnicodeButton(text=str(i), on_press=self.press_key))
        btns.add_widget(UnicodeButton(text="⌫", on_press=self.press_back, on_release=self.press_back))
        btns.add_widget(UnicodeButton(text="0", on_press=self.press_key))
        btns.add_widget(UnicodeButton(text="↩", on_press=self.press_enter))        
        
        layout.add_widget(self.textinput)
        layout.add_widget(btns)
        
        return layout
    
    
    def get_next_state(self, inp=""):
        if self.current_state == "waiting for washer id":
            self.label1.text = "LaundryPiBot"
            
            if inp == "":
                self.label2.text = "Please input the id of the washer that you would like to be notified of."
                
            elif not laundrypidb.is_valid_washer(inp):
                self.label2.text = "Invalid washer id! Please input the number printed on the washer."
            
            else:
                self.chosen_washer_id = int(inp)
                
                if laundrypidb.get_washer_state(self.chosen_washer_id) == "faulty":
                    self.label2.text = "Washer {} has been reported as faulty. Please try another washer!".format(self.chosen_washer_id)                   
                    self.chosen_washer_id = None
                
                else:
                    self.current_state = "waiting for phone num"
                    self.get_next_state()
        
        elif self.current_state == "waiting for phone num":
            self.label1.text = "Chosen washer: {}".format(self.chosen_washer_id)
            
            if inp == "":
                self.label2.text = "Please input your phone number so that we can contact you via LaundryPiBot on Telegram."
            
            else:
                chat_id = self.get_chat_id(inp)
                if not chat_id:
                    self.label2.text = "Invalid phone number! You need to share your contact with LaundryPiBot on Telegram by running /start before you can use this service."

                else:
                    reply = self.update_waitlist(self.chosen_washer_id, chat_id)
                    self.label1.text = "LaundryPiBot"
                    self.label2.text = "Thank you for using LaundryPiBot! " + reply
                    
                    self.current_state = "waiting for washer id"
                    self.chosen_washer_id = None
                    
                    delay = 4.5
                    Clock.schedule_once(lambda dt: self.get_next_state(), delay)
    
    
    def _update_labels(self, instance, width):
        self.label1.text_size = (width, None)
        self.label2.text_size = (width, None)
    
    
    def press_key(self, btn):        
        self.textinput.insert_text(btn.text)
    
    
    def press_back(self, btn):
        if btn.state == "normal":
            self.textinput.release_backspace()
        
        elif self.textinput.text != "":
            self.textinput.press_backspace()
        
        elif self.current_state == "waiting for phone num":
            self.current_state = "waiting for washer id"
            self.get_next_state()
    
    
    def press_enter(self, btn):
        self.get_next_state(self.textinput.text)
        self.textinput.text = ""
    
    
    def get_chat_id(self, phone_num):
        return laundrypidb.get_chat_id(phone_num)
    
    
    def update_waitlist(self, washer_id, chat_id):
        reply = laundrypidb.update_waitlist(washer_id, chat_id)
        laundrypibot.send_kivy_notification(chat_id, washer_id)
        return reply


def main():
    LaundryPiApp().run()


if __name__ == '__main__':
    main()

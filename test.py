from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import ObjectProperty, NumericProperty
from kivy.graphics.texture import Texture
import time
import threading

import cv2
# import mediapipe as mp

class MenuScreen(Screen):
    def __init__(self,**kwargs):
        super().__init__()
        res = self.build()
        self.ids.menu_screen_box.add_widget(res)
    
    def build(self):
        self.img1=Image()
        self.img1.allow_stretch=True
        layout = BoxLayout()
        layout.add_widget(self.img1)
        #opencv2 stuffs
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.capture.set(cv2.CAP_PROP_FPS, 30.0)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        # cv2.namedWindow("CV2 Image")
        Clock.schedule_interval(self.update, 1.0/33.0)
        return layout

    def update(self, dt):
        # display image from cam in opencv window
        ret, frame = self.capture.read()
        # cv2.imshow("CV2 Image", frame)
        # convert it to texture
        buf1 = cv2.flip(frame, -1)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
        #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer. 
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1


class TestApp(App):
    def build(self):
        kv = Builder.load_file('screens.kv')
        return kv

if __name__ == '__main__':
    TestApp().run()

# class CamApp(App):

#     def build(self):
#         self.img1=Image()
#         self.img1.allow_stretch=True
#         layout = BoxLayout()
#         layout.add_widget(self.img1)
#         #opencv2 stuffs
#         self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#         self.capture.set(cv2.CAP_PROP_FPS, 30.0)
#         self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
#         self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
#         self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#         self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
#         # cv2.namedWindow("CV2 Image")
#         Clock.schedule_interval(self.update, 1.0/33.0)
#         return layout

#     def update(self, dt):
#         # display image from cam in opencv window
#         ret, frame = self.capture.read()
#         # cv2.imshow("CV2 Image", frame)
#         # convert it to texture
#         buf1 = cv2.flip(frame, -1)
#         buf = buf1.tostring()
#         texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
#         #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer. 
#         texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
#         # display image from the texture
#         self.img1.texture = texture1

# if __name__ == '__main__':
#     CamApp().run()
#     cv2.destroyAllWindows()
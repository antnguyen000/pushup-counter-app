from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

import cv2
import mediapipe as mp

class CamApp(App):

    def build(self):
        self.img1=Image()
        layout = BoxLayout()
        layout.add_widget(self.img1)
        #opencv2 stuffs
        self.capture = cv2.VideoCapture(0)
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

class openCVApp():

    def detector_objectifier():
        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose

        pose = mp_pose.Pose(min_detection_confidence=.5, min_tracking_confidence=.5)

        return mp_drawing, pose

    def video_detection(video_file, mp_drawing, pose):
        cap = cv2.VideoCapture(video_file)
        
        while cap.isOpened():
            _, frame = cap.read()

            # try:
            #     RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # except:
            #     break

            results = pose.process(RGB)
            print(results.pose_landmarks)

            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow("Output", frame)

            if cv2.waitKey(1) == ord("q"):
                break

            cap.release()
            cv2.destroyAllWindows()

            


if __name__ == '__main__':
    CamApp().run()
    cv2.destroyAllWindows()
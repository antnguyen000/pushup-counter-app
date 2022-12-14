import PySimpleGUI as sg
import cv2
import numpy as np
import mediapipe as mp
import time, math
import pushup_type
import pyglet
import pyttsx3


def main():

    sg.theme('DarkTeal')
    engine = pyttsx3.init()

    # define the window layout
    layout1 = [[sg.Column([
                [sg.Image(filename='large_logo.png')]], justification='center')],
                [sg.Column([
                [sg.Button('Start'), sg.Button('Exit')]], justification='center')]]

    layout2 = [[sg.Column([
                [sg.Image(filename='large_logo.png')]], justification='center')],
                [sg.Column([[sg.Text('Select Camera View:'),
                sg.Button('Front Facing Camera'),
                sg.Button('Side Facing Camera')],[
                sg.Column([[sg.Button('Return')]], justification='center')]], justification='center')]]

    layout3 = [[sg.Button('Go Back')],
            [sg.Image(filename='', key='image')]]
    
            
    layout = [[sg.Column(layout1, key='-COL1-'), sg.Column(layout2, visible=False, key='-COL2-'), sg.Column(layout3, visible=False, key='-COL3-')]]

    # create the window and show it without the plot
    window = sg.Window('OpenCV Pushup Tracker',
                       layout, finalize=True, element_justification='center')

    window.maximize()

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #

    recording = False

    layout = 1

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    pose = mp_pose.Pose(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # Initializing pushup counter
    pushup_count = 0
    pushup_position = 1 # Assuming start position is up

    # Initializing Start countdown
    start_pushup = False
    start_countdown = False

    while True:
        event, values = window.read(timeout=20)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break


        elif event == 'Front Facing Camera' or event == 'Side Facing Camera':
            window[f'-COL{layout}-'].update(visible=False)
            layout += 1
            window[f'-COL{layout}-'].update(visible=True)
            recording = True
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FPS, 30.0)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            start_pushup = False
            start_countdown = False
            pushup_count = 0
            if event == 'Front Facing Camera':
                pushupView = 'Front View'
            if event == 'Side Facing Camera':
                pushupView = 'Side View'

        elif event == 'Start':
            window[f'-COL{layout}-'].update(visible=False)
            layout += 1
            window[f'-COL{layout}-'].update(visible=True)

        elif event == 'Go Back':
            img = np.full((480, 640), 255)
            # this is faster, shorter and needs less includes
            imgbytes = cv2.imencode('.png', img)[1].tobytes()
            window['image'].update(data=imgbytes)
            recording = False
            cap = None
            window[f'-COL{layout}-'].update(visible=False)
            layout -= 1
            window[f'-COL{layout}-'].update(visible=True)

        elif event == 'Return':
            window[f'-COL{layout}-'].update(visible=False)
            layout -= 1
            window[f'-COL{layout}-'].update(visible=True)
                        
            
        if recording:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)

            if not start_countdown:
                # Record initial time step and countdown for 10 seconds
                timestamp0 = time.time()
                start_countdown = True

            # Pushup countdown code
            if not start_pushup:
                curr = time.time()
                res = curr - timestamp0
                if res > 10:
                    start_pushup = True

                # Reducing frame opacity    
                frame = np.array(frame, dtype=float)
                frame /= 2.0

                cv2.putText(frame, "Get in Position!", (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/8), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/4)), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 5, cv2.LINE_AA)
                cv2.putText(frame, str(math.ceil(10 - (curr-timestamp0))), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2 - 100), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2 + 150)), cv2.FONT_HERSHEY_SIMPLEX, 10, (255, 255, 255), 5, cv2.LINE_AA)

                if pushupView == "Side View":
                    cv2.putText(frame, "Feet", (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/5 - 150), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(frame, "Head", (int(4*cap.get(cv2.CAP_PROP_FRAME_WIDTH)/5), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

                imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
                window['image'].update(data=imgbytes)

                
            else:  
                try:
                    # convert the frame from BGR -> RGB format for mediapipe processing
                    frame.flags.writeable = False
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # process the RGB frame to get detection model
                    results = pose.process(image)

                    # Convert image from RGB -> BGR
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    
                    # Extracting specific landmarks for excercises
                    try:
                        landmarks = results.pose_landmarks.landmark
                        
                        if pushupView == 'Front View':
                        # Runs the selected pushup type
                            left_angle, right_angle, image = pushup_type.frontview_pushup(image, landmarks, mp_pose, cap)
                        
                        # FRONTVIEW pushup counter: Counts when left & right elbow angle is below 90deg and above 170deg
                            if pushup_position and left_angle <= 90 and right_angle <= 90:
                                pushup_position = 0
                                engine.save_to_file('UP', 'test.wav')
                                engine.runAndWait()
                                filename = 'test.wav'
                                music = pyglet.media.load(filename, streaming=False)
                                music.play()
                                music.delete()


                            elif not pushup_position and left_angle >= 170 and right_angle >= 170:
                                pushup_position = 1
                                pushup_count += 1
                                engine.save_to_file(f'{pushup_count}, DOWN', 'test.wav')
                                engine.runAndWait()
                                filename = 'test.wav'
                                music = pyglet.media.load(filename, streaming=False)
                                music.play()
                                music.delete()

                        if pushupView == 'Side View':
                            elbow_angle, back_angle, image = pushup_type.sideview_pushup(image, landmarks, mp_pose, cap)
                        # SIDEVIEW pushup counter: Counts when elbow angle is below 90deg and above 160deg while back is maintained at above 150deg
                            if pushup_position and elbow_angle <= 90 and back_angle >= 150:
                                pushup_position = 0
                                engine.save_to_file('UP', 'test.wav')
                                engine.runAndWait()
                                filename = 'test.wav'
                                music = pyglet.media.load(filename, streaming=False)
                                music.play()
                                music.delete()
                            elif not pushup_position and elbow_angle >= 160 and back_angle >= 150:
                                pushup_position = 1
                                pushup_count += 1
                                engine.save_to_file(f'{pushup_count}, DOWN', 'test.wav')
                                engine.runAndWait()
                                filename = 'test.wav'
                                music = pyglet.media.load(filename, streaming=False)
                                music.play()
                                music.delete()
                        
                        # Putting the pushup count on the image
                        cv2.putText(image, pushupView, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) - 700), 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                        cv2.putText(image, str(pushup_count), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                        if pushup_position:
                            cv2.putText(image, "DOWN", (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) - 100), 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                        else:
                            cv2.putText(image, "UP", (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) - 100), 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                    except:
                        pass
                    
                    # Draw landmarks (joints and connections) onto the image
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                                mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=1, circle_radius=0),
                                                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=3, circle_radius=2)
                                                )

                    imgbytes = cv2.imencode('.png', image)[1].tobytes()  # ditto
                    window['image'].update(data=imgbytes)
                except:
                    break
        else:
            pushup_count = 0

    window.close()

if __name__ == '__main__':
    main()
import PySimpleGUI as sg
import cv2
import numpy as np
import mediapipe as mp
import time, math

import pushup_type

def main():

    # sg.theme('Black')

    # define the window layout
    layout1 = [[sg.Text('Pushup Analyzer'),
                sg.Text('By: The Probers'),
                sg.Button('Start'), sg.Button('Exit')]]

    layout2 = [[sg.Text('Pushup Analyzer'),
                sg.Text('By: The Probers'),
                sg.Button('Return')],
                [sg.Button('Front Facing Camera'),
                sg.Button('Side Facing Camera')]]

    layout3 = [[sg.Text('Pushup Analyzer'),
                sg.Text('By: The Probers'),
                sg.Button('Go Back')],
            [sg.Image(filename='', key='image')]]
    
            
    layout = [[sg.Column(layout1, key='-COL1-'), sg.Column(layout2, visible=False, key='-COL2-'), sg.Column(layout3, visible=False, key='-COL3-')]]

    # create the window and show it without the plot
    window = sg.Window('OpenCV Pushup Tracker',
                       layout, finalize=True)

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
                
                cv2.putText(frame, str(math.ceil(10 - (curr-timestamp0))), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2 - 100), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2 + 100)), cv2.FONT_HERSHEY_SIMPLEX, 10, (255, 255, 255), 5, cv2.LINE_AA)
            
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
                        
                        # Runs the selected pushup type
                        left_angle, right_angle, image = pushup_type.frontview_pushup(image, landmarks, mp_pose, cap)
                        # elbow_angle, back_angle, image = pushup_type.sideview_pushup(image, landmarks, mp_pose, cap)
                        
                        # FRONTVIEW pushup counter: Counts when left & right elbow angle is below 90deg and above 170deg
                        if pushup_position and left_angle <= 90 and right_angle <= 90:
                            pushup_position = 0
                        elif not pushup_position and left_angle >= 170 and right_angle >= 170:
                            pushup_position = 1
                            pushup_count += 1

                        # SIDEVIEW pushup counter: Counts when elbow angle is below 90deg and above 160deg while back is maintained at above 155deg
                        # if pushup_position and elbow_angle <= 90 and back_angle >= 155:
                        #     pushup_position = 0
                        # elif not pushup_position and elbow_angle >= 160 and back_angle >= 155:
                        #     pushup_position = 1
                        #     pushup_count += 1 
                        
                        # Putting the pushup count on the image
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

    window.close()

    # # ----------- Create the 3 layouts this Window will display -----------
    # layout1 = [[sg.Text('This is layout 1 - It is all Checkboxes')],
    #         *[[sg.CB(f'Checkbox {i}')] for i in range(5)]]

    # layout2 = [[sg.Text('This is layout 2')],
    #         [sg.Input(key='-IN-')],
    #         [sg.Input(key='-IN2-')]]

    # layout3 = [[sg.Text('This is layout 3 - It is all Radio Buttons')],
    #         *[[sg.R(f'Radio {i}', 1)] for i in range(8)]]

    # # ----------- Create actual layout using Columns and a row of Buttons
    # layout = [[sg.Column(layout1, key='-COL1-'), sg.Column(layout2, visible=False, key='-COL2-'), sg.Column(layout3, visible=False, key='-COL3-')],
    #         [sg.Button('Cycle Layout'), sg.Button('1'), sg.Button('2'), sg.Button('3'), sg.Button('Exit')]]

    # window = sg.Window('Swapping the contents of a window', layout)

    # layout = 1  # The currently visible layout
    # while True:
    #     event, values = window.read()
    #     print(event, values)
    #     if event in (None, 'Exit'):
    #         break
    #     if event == 'Cycle Layout':
    #         window[f'-COL{layout}-'].update(visible=False)
    #         layout = layout + 1 if layout < 3 else 1
    #         window[f'-COL{layout}-'].update(visible=True)
    #     elif event in '123':
    #         window[f'-COL{layout}-'].update(visible=False)
    #         layout = int(event)
    #         window[f'-COL{layout}-'].update(visible=True)
    # window.close()

if __name__ == '__main__':
    main()
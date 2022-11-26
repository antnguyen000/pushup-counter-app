import PySimpleGUI as sg
import cv2
import numpy as np
import mediapipe as mp

def main():

    sg.theme('Black')

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
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FPS, 30.0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def calc_angle(a, b, c):
        a = np.array(a)
        b = np.array(b) # Mid point
        c = np.array(c)

        ba = a - b
        bc = c - b

        angle = np.degrees(np.arccos(np.dot(a-b, c-b) / (np.linalg.norm(a-b) * np.linalg.norm(c-b))))

        if angle > 180:
            angle = 360 - angle

        return angle

    while True:
        event, values = window.read(timeout=20)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break

        elif event == 'Front Facing Camera' or event == 'Side Facing Camera':
            window[f'-COL{layout}-'].update(visible=False)
            layout += 1
            window[f'-COL{layout}-'].update(visible=True)
            recording = True

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
                    # Extracting specific joint coordinates from the array of landmarks -> mp_pose.PoseLandmark.{BODYPART}.value
                    # Example to get x & y from left elbow -> [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

                    # For front view pushups - main points: (LEFT_WRIST, LEFT_ELBOW, LEFT_SHOULDER) & (RIGHT_WRIST, RIGHT_ELBOW, RIGHT_SHOULDER)
                    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

                    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

                    # Calculating angles
                    left_angle = round(calc_angle(left_wrist, left_elbow, left_shoulder))
                    right_angle = round(calc_angle(right_wrist, right_elbow, right_shoulder))

                    # Putting text onto the camera
                    cv2.putText(image, str(left_angle), tuple(np.multiply(left_elbow, [cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(image, str(right_angle), tuple(np.multiply(right_elbow, [cap.get(cv2.CAP_PROP_FRAME_WIDTH) - 250, cap.get(cv2.CAP_PROP_FRAME_HEIGHT)]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                except:
                    pass
                
                # Draw landmarks (joints and connections) onto the image
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

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
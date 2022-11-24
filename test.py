import PySimpleGUI as sg
import cv2
import numpy as np

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
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['image'].update(data=imgbytes)
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
import cv2
import numpy as np
import mediapipe as mp

# Front view pushup selection
# Output: Left & right angle, and image on the frame
def frontview_pushup(image, landmarks, mp_pose, cap):
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
    left_angle = round(calc_angle(left_shoulder, left_elbow, left_wrist))
    right_angle = round(calc_angle(right_shoulder, right_elbow, right_wrist))

    # Putting text onto the camera
    cv2.putText(image, str(left_angle), tuple(np.multiply(left_elbow, [cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, str(right_angle), tuple(np.multiply(right_elbow, [cap.get(cv2.CAP_PROP_FRAME_WIDTH) - 250, cap.get(cv2.CAP_PROP_FRAME_HEIGHT)]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

    return left_angle, right_angle, image


# Sideview assums feet point to the left & head points to the right side of the screen
def sideview_pushup(image, landmarks, mp_pose, cap):
    # Extracting specific joint coordinates from the array of landmarks -> mp_pose.PoseLandmark.{BODYPART}.value
    # Example to get x & y from left elbow -> [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

    # For side view pushups - main points: (RIGHT_WRIST, RIGHT_ELBOW, RIGHT_SHOULDER) & (RIGHT_SHOULDER, RIGHT_HIP, RIGHT_ANKLE)
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    
    # Calculating angles
    elbow_angle = round(calc_angle(left_shoulder, left_elbow, left_wrist))
    back_angle = round(calc_angle(left_shoulder, left_hip, left_ankle))

    # Putting text onto the camera - Places text on right elbow & hip due to camera flip
    cv2.putText(image, str(elbow_angle), tuple(np.multiply(right_elbow, [cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, str(back_angle), tuple(np.multiply(right_hip, [cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 200]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

    return elbow_angle, back_angle, image

def calc_angle(a, b, c):
        a = np.array(a)
        b = np.array(b) # Mid point
        c = np.array(c)

        angle = np.degrees(np.arccos(np.dot(a-b, c-b) / (np.linalg.norm(a-b) * np.linalg.norm(c-b))))

        if angle > 180:
            angle = 360 - angle

        return angle
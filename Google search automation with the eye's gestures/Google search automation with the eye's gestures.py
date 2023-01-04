import cv2
import numpy as np
import dlib
from math import hypot
import pyglet
import time 
# Load sounds
sound = pyglet.media.load("sound.wav", streaming = False)
left_sound = pyglet.media.load("left.wav", streaming = False)
right_sound = pyglet.media.load("right.wav", streaming = False)

cap = cv2.VideoCapture(0)

board = np.zeros((300, 600), np.uint8)
board[:]= 255

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

#keyboard settings
keyboard = np.zeros((600, 750, 3), np.uint8)

keys_set_1 = {0: "Q", 1: "W", 2: "E", 3: "R", 4: "T",
              5: "A", 6: "S", 7: "D", 8: "F", 9: "G",
              10: "Z", 11: "X", 12: "C", 13: "V", 14: "B"}
keys_set_2 = {0: "Y", 1: "U", 2: "I", 3: "O", 4: "P",
              5: "H", 6: "J", 7: "K", 8: "L", 9: "_",
              10: "V", 11: "B", 12: "N", 13: "M", 14: "<"}

def draw_letters(letter_index, text, letter_light):
    # Keys
    if letter_index == 0:
        x = 0
        y = 0
    elif letter_index == 1:
        x = 150
        y = 0
    elif letter_index == 2:
        x = 300
        y = 0
    elif letter_index == 3:
        x = 450
        y = 0
    elif letter_index == 4:
        x = 600
        y = 0
    elif letter_index == 5:
        x = 0
        y = 200
    elif letter_index == 6:
        x = 150
        y = 200
    elif letter_index == 7:
        x = 300
        y = 200
    elif letter_index == 8:
        x = 450
        y = 200
    elif letter_index == 9:
        x = 600
        y = 200
    elif letter_index == 10:
        x = 0
        y = 400
    elif letter_index == 11:
        x = 150
        y = 400
    elif letter_index == 12:
        x = 300
        y = 400
    elif letter_index == 13:
        x = 450
        y = 400
    elif letter_index == 14:
        x = 600
        y = 400

    width = 150
    height = 200
    th = 3 # thickness
    if letter_light is True:
        cv2.rectangle(keyboard, (x + th, y + th), (x + width - th, y + height - th), (255, 255, 255), -1)
    else:
        cv2.rectangle(keyboard, (x + th, y + th), (x + width - th, y + height - th), (255, 0, 0), th)

    # Text settings
    font_letter = cv2.FONT_HERSHEY_PLAIN
    font_scale = 10
    font_th = 4
    text_size = cv2.getTextSize(text, font_letter, font_scale, font_th)[0]
    width_text, height_text = text_size[0], text_size[1]
    text_x = int((width - width_text) / 2) + x
    text_y = int((height + height_text) / 2) + y
    cv2.putText(keyboard, text, (text_x, text_y), font_letter, font_scale, (255, 0, 0), font_th)


def get_eye_region(eye_points, facial_landmarks):
    eye_region = np.array([(facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),
                                (facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),
                                (facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),
                                (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),
                                (facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),
                                (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)], np.int32)
    cv2.polylines(frame, [eye_region], True, (0, 0, 255), 2)

    return eye_region

    
def draw_menu():
    rows, cols, _ = keyboard.shape
    th_lines = 4 # thickness lines
    cv2.line(keyboard, (int(cols/2) - int(th_lines/2), 0),(int(cols/2) - int(th_lines/2), rows),
             (51, 51, 51), th_lines)
    cv2.putText(keyboard, "LEFT", (80, 300), font, 6, (255, 255, 255), 5)
    cv2.putText(keyboard, "RIGHT", (80 + int(cols/2), 300), font, 6, (255, 255, 255), 5)

    
def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

font = cv2.FONT_HERSHEY_PLAIN

def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

    #hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
    #ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))
    
    if ver_line_lenght!=0:
        ratio = hor_line_lenght / ver_line_lenght
        return ratio

def get_gaze_ratio(eye_points, facial_landmarks):
    eye_region = np.array([(facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),
                                (facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),
                                (facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),
                                (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),
                                (facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),
                                (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)], np.int32)
    cv2.polylines(frame, [eye_region], True, (0, 0, 255), 2)

    height, width, _ = frame.shape
    mask = np.zeros((height, width), np.uint8)
    cv2.polylines(mask, [eye_region], True, 255, 2)
    cv2.fillPoly(mask, [eye_region], 255)
    eye = cv2.bitwise_and(gray, gray, mask=mask)

    min_x = np.min(eye_region[:, 0])
    max_x = np.max(eye_region[:, 0])
    min_y = np.min(eye_region[:, 1])
    max_y = np.max(eye_region[:, 1])

    gray_eye = eye[min_y:max_y, min_x:max_x]
    _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
    height, width = threshold_eye.shape
    left_side_threshold = threshold_eye[0: height, 0: int(width / 2)]
    left_side_white = cv2.countNonZero(left_side_threshold)

    right_side_threshold = threshold_eye[0: height, int(width / 2): width]
    right_side_white = cv2.countNonZero(right_side_threshold)

    if left_side_white == 0:
        gaze_ratio = 1
    elif right_side_white == 0:
        gaze_ratio = 5
    else:
        gaze_ratio = left_side_white / right_side_white
    return gaze_ratio


#counters
frames = 0
letter_index = 0
blinkings_frames = 0
text = ""
keyboard_selected = "left"
last_keyboard_selected="left"
select_keyboard_menu = True
keyboard_selection_frames=0
while True:
    _, frame = cap.read()
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
    keyboard[:] =(26, 26, 26)
    frames +=1 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    new_frame = np.zeros((300, 300, 3), np.uint8)
    faces = detector(gray)
    
    
    if select_keyboard_menu is True:
        draw_menu()
    
    # Keyboard selected
    if keyboard_selected == "left":
        keys_set = keys_set_1
    else:
        keys_set = keys_set_2
    active_letter = keys_set[letter_index]

    
    for face in faces:
        #x, y = face.left(), face.top()
        #x1, y1 = face.right(), face.bottom()
        #cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)

        landmarks = predictor(gray, face)
        
        
        #detect blinking 
        left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2
       
        eye_region_left=get_eye_region([36, 37, 38, 39, 40, 41], landmarks)
        eye_region_right=get_eye_region([42, 43, 44, 45, 46, 47], landmarks)
        
        if select_keyboard_menu is True:

            #gaze detection
            gaze_ratio_left_eye = get_gaze_ratio([36, 37, 38, 39, 40, 41], landmarks)
            gaze_ratio_right_eye = get_gaze_ratio([42, 43, 44, 45, 46, 47], landmarks)

            gaze_ratio_avg = (gaze_ratio_right_eye + gaze_ratio_left_eye) / 2
            #cv2.putText(frame, str(gaze_ratio_avg), (50, 100), font, 2, (0, 0, 255), 3)
       
            if gaze_ratio_avg >1.5:
                                       
                                        #cv2.putText(frame, "LEFT", (40, 100), font, 2, (255, 0, 0), 3)
                                        #new_frame[:] = (255, 0, 0)
                keyboard_selected = "left"
                keyboard_selection_frames += 1
                # If Kept gaze on one side more than 15 frames, move to keyboard
                if keyboard_selection_frames == 15:
                    select_keyboard_menu = False
                    left_sound.play()
                    keyboard_selection_frames = 0

                    # Set frames count to 0 when keyboard selected
                    frames = 0
                if keyboard_selected!=last_keyboard_selected:
                    last_keyboard_selected = keyboard_selected
                    keyboard_selection_frames = 0
               

            elif gaze_ratio_avg <0.8:
                                        #cv2.putText(frame, "RIGHT", (40, 100), font, 2, (0, 0, 255), 3)
                                        #new_frame[:] = (0, 0, 255)
                keyboard_selected = "right"
                keyboard_selection_frames += 1
               
                # If Kept gaze on one side more than 15 frames, move to keyboard
                if keyboard_selection_frames == 15:
                    select_keyboard_menu = False
                    right_sound.play()
                    # Set frames count to 0 when keyboard selected
                    frames = 0 
                if keyboard_selected!=last_keyboard_selected:
                    last_keyboard_selected = keyboard_selected
                    keyboard_selection_frames = 0
        else:
            if blinking_ratio > 5:
                cv2.putText(frame, "BLINKING", (50, 150), font, 4, (255, 0, 0), thickness = 3)
                blinkings_frames += 1 
                frames -= 1
                cv2.polylines(frame, [eye_region_left], True, (0, 255, 0), 2)
                cv2.polylines(frame, [eye_region_right], True, (0, 255, 0), 2)
                #Typing letter
                if blinkings_frames == 3:
                    text += active_letter
                    sound.play()
                    time.sleep(1)
                    select_keyboard_menu = True

            else:
                blinkings_frames = 0
                    
        #cv2.putText(frame, str(gaze_ratio_avg), (50, 100), font, 2, (0, 0, 255), 3)
        #cv2.putText(frame, str(right_side_white), (50, 150), font, 2, (0, 0, 255), 3)
        
    

    # Display letters on the keyboard
    if select_keyboard_menu is False:
        if frames == 25:
            letter_index += 1
            frames = 0
        if letter_index == 15:
            letter_index = 0
        for i in range(15):
            if i == letter_index:
                light = True
            else:
                light = False
            draw_letters(i, keys_set[i], light)

    
    
    cv2.putText(board, text, (10,70), font, 4, 0, 3)

    cv2.imshow("Frame", frame)
    #cv2.imshow("Newframe", new_frame)
    cv2.imshow("Vertual_keyboard", keyboard)
    cv2.imshow("Board", board)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()

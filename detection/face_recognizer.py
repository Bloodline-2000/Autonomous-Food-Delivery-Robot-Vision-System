import face_recognition
import cv2
import os
import numpy as np
import time


# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)
print('streaming now')

# Initialize some variables
face_locations = []
face_encodings = []
process_this_frame = 0

total_time = 0
frame_cnt = 0
detect_times = 0
while True:
    # Grab a single frame of video
    start_time = time.time()
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]
    # rgb_small_frame = frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame == 2:
        process_this_frame = 0
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        frame_cnt += 1

    process_this_frame += 1
    total_time += (time.time()-start_time)

    # Display the results
    for (top, right, bottom, left) in face_locations:
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        cv2.rectangle(frame, (left*2, top*2), (right*2, bottom*2), (0, 0, 255), 2)
    if len(face_locations)>0:
        detect_times += 1
        print('detected')

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if total_time>10:
        break

print("frame rate", frame_cnt/total_time)
print("detect times", detect_times)
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
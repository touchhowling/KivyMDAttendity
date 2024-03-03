import cv2
import numpy as np
import face_recognition
import os
import csv
from datetime import datetime
import pickle
import pandas as pd
import logging



logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='backend.log', level=logging.DEBUG)


def process_attendance(video_path, class_name):
    with open('hello_world.txt', 'w') as file:
        file.write('Hello, World!')
    class_name_c=class_name
    logging.info(f"Processing attendance ")
    train_dir = f'database/{class_name}'
    train_images = []
    classNames = []
    rollNumbers = []
    classes = []
    myList = os.listdir(train_dir)
    for cl in myList:
        curImg = cv2.imread(os.path.join(train_dir, cl))
        train_images.append(curImg)
        parts = os.path.splitext(cl)[0].split('_')
        if len(parts) >= 3:
            name = '_'.join(parts[:-2])
            roll_number = parts[-2]
            class_name = parts[-1]
        else:
            name = parts[0]
            roll_number = ""
            class_name = ""
        classNames.append(name)
        rollNumbers.append(roll_number)
        classes.append(class_name)

    with open(os.path.join('database', class_name, 'encodeListKnown.pkl'), 'rb') as file:
        encodeListKnown = pickle.load(file)

    video_capture = cv2.VideoCapture(video_path)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    print(fps)
    frames_to_skip = 9*int(round(fps / 1))
    print(frames_to_skip)
    attendance_data = []
    processed_names = set()
    frame_count = 0

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        frame_count += 1
        print(frame_count)

        if frame_count % frames_to_skip != 0:
            continue

        input_image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(input_image_rgb, model="cnn")

        print(f"Number of Faces Detected: {len(face_locations)}")

        encodings = face_recognition.face_encodings(input_image_rgb, face_locations)

        for face_encoding, face_location in zip(encodings, face_locations):
            matches = face_recognition.compare_faces(encodeListKnown, face_encoding)
            face_distances = face_recognition.face_distance(encodeListKnown, face_encoding)

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = classNames[best_match_index]
                    roll_number = rollNumbers[best_match_index]
                    class_name = classes[best_match_index]

                    # Skip if name is empty
                    if not name:
                        continue

                    if name in processed_names:
                        continue

                    processed_names.add(name)

                    attendance_data.append([name, roll_number, class_name, 'P'])

                    top, right, bottom, left = face_location
                    # cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    # cv2.putText(frame, f'{name} ({roll_number}, {class_name}, P)', (left + 6, bottom - 6),
                    #             cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                else:
                    # cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]),
                    #               (0, 0, 0), cv2.FILLED)
                    attendance_data.append([name, roll_number, class_name, 'A'])

    video_capture.release()

    # Create or update the attendance file
    attendance_file = os.path.join('database', class_name_c, f'Attendance_{class_name_c}.xlsx')
    if os.path.exists(attendance_file):
        # If the file exists, load it and update with the new data
        attendance_df = pd.read_excel(attendance_file)

        # Add a new column for the current date if not already present
        current_date = datetime.now().strftime('%d-%m-%Y')
        if current_date not in attendance_df.columns:
            attendance_df[current_date] = ''

        # Update attendance information
        for data in attendance_data:
            name, _, _, status = data
            attendance_df.loc[attendance_df['Name'] == name, current_date] = status

        # Save the updated DataFrame to the file
        attendance_df.to_excel(attendance_file, index=False)
    else:
        # If the file doesn't exist, create a new one
        attendance_df = pd.DataFrame(attendance_data, columns=['Name', 'Roll Number', 'Class', 'Attendance'])
        attendance_df['Date'] = datetime.now().strftime('%d-%m-%Y')
        attendance_df.to_excel(attendance_file, index=False)

    # Print the contents of the updated Excel file
    attendance_df_read = pd.read_excel(attendance_file)
    print(attendance_df_read)

# Example usage
# process_attendance('20230724_124411.mp4', 'Iot')

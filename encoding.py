import cv2
import numpy as np
import face_recognition
import os
import pickle

def encode_faces_for_class(class_name):
    class_dir = os.path.dirname(os.path.abspath(__file__))
    class_dir=f'{class_dir}\\database\\{class_name}'
    train_images = []
    classNames = []
    rollNumbers = []
    classes = []
    encodeListKnown = []

    # Load images
    myList = [cl for cl in os.listdir(class_dir) if cl.lower().endswith('.jpg')]
    for cl in myList:
        print(cl)
        curImg = cv2.imread(os.path.join(class_dir, cl))
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

    # Encode faces
    for img in train_images:
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(img)
            if len(face_encodings) > 0:
                encodeListKnown.append(face_encodings[0])

    # Save encoding to file
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)

    with open(os.path.join(class_dir, 'encodeListKnown.pkl'), 'wb') as file:
        pickle.dump(encodeListKnown, file)

    print(f'Encoding for class {class_name} saved to {class_name}')

if __name__ == "__main__":
    class_name_to_encode_and_save = 'iot'
    encode_faces_for_class(class_name_to_encode_and_save)


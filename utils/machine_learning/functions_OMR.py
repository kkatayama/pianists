#!/usr/bin/env python3
from pathlib import Path
import tensorflow as tf
import numpy as np
import argparse
import cv2
import sys
import os
import json


all_notes = ['C1', 'CS1', 'D1', 'DS1', 'E1', 'F1', 'FS1', 'G1', 'GS1', 'A1',  'AS1', 'B1', 'C2', 'CS2', 'D2', 'DS2', 'E2',
'F2', 'FS2', 'G2', 'GS2', 'A2', 'AS2', 'B2', 'C3', 'CS3', 'D3', 'DS3', 'E3', 'F3', 'FS3', 'G3', 'GS3', 'A3', 'AS3', 'B3',
'C4', 'CS4', 'D4', 'DS4', 'E4', 'F4', 'FS4', 'G4', 'GS4', 'A4', 'AS4', 'B4', 'C5', 'CS5', 'D5', 'DS5', 'E5', 'F5', 'FS5',
'G5', 'GS5', 'A5', 'AS5', 'B5', 'C6', 'CS6', 'D6', 'DS6', 'E6', 'F6', 'FS6', 'G6', 'GS6', 'A6', 'AS6', 'B6',  'C7' ]

def binary_convert(image):
    """Reads image and coonverts it to black and white (binary) image"""
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    return thresh

def line_detect_and_remove(original_image, line_image):
    """Detects, removes, and repairs resulting image after removing lines"""
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50,1))
    detected_lines = cv2.morphologyEx(line_image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(image, [c], -1, (255,255,255), 2)

    repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,6))
    result = 255 - cv2.morphologyEx(255 - original_image, cv2.MORPH_CLOSE, repair_kernel, iterations=1)

    return result, cnts

def extract_individual_image(image, no_line, contours):
    """Takes original image and list of contours and creates individual image of each"""
    cntr_index_LtoR = np.argsort([cv2.boundingRect(i)[0] for i in contours])
    file_save_count = 0

    for index in range(len(cntr_index_LtoR)):
        contour_index_val = cntr_index_LtoR[index]
        dimensions = image.shape
        x = dimensions[0] #Store x
        y = dimensions[1] #Store y

        im2 =  np.zeros((x,y,3), np.uint8)
        cv2.drawContours(im2, contours, contour_index_val, (255,255,255), cv2.FILLED)
        im2 = cv2.bitwise_and(im2, no_line)
        c = contours[contour_index_val]

        extLeft = tuple(c[c[:, :, 0].argmin()][0])
        extRight = tuple(c[c[:, :, 0].argmax()][0])
        extTop = tuple(c[c[:, :, 1].argmin()][0])
        extBot = tuple(c[c[:, :, 1].argmax()][0])

        x_mean = (extRight[0] + extLeft[0]) / 2
        y_mean = (extBot[1] + extTop[1]) / 2

        if y_mean > 50:
            shift_y = 50 - y_mean
        elif y_mean < 50:
            shift_y = 50 - y_mean
        if x_mean > 100:
            shift_x = 100 - x_mean
        elif x_mean < 100:
            shift_x = 100 - x_mean

        M = np.float32([ #Matrix used for shifting operation
            [1, 0, shift_x],
            [0, 1, shift_y]])

        shifted_image = cv2.warpAffine(im2, M, (im2.shape[1], im2.shape[0])) #Shift transformation
        final_image = shifted_image[0:200, 0:200]
        output_filename = "{}.png".format(file_save_count)
        # output_filepath = os.path.join("/Users/nick-kater/Desktop/feeding/", output_filename)
        output_filepath = Path(Path.cwd().joinpath("cropped"), output_filename).as_posix()
        final_image = ~final_image
        file_save_count += 1
        cv2.imwrite(output_filepath, final_image)

    return cntr_index_LtoR

def extract_contours(bw):
    """Takes black background binary image and finds contours, returns list of contours"""
    contours = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]

    return contours

def order_sort(folder):
    """Sorts files in order of filesname"""

    files = []
    for image in os.listdir(folder):
        if image == ".DS_Store":
            pass
        else:
            files.append(image)

    sorted_files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))

    sorted_filepaths = []

    for file in sorted_files:
        filepath = os.path.join(folder, file)
        sorted_filepaths.append(filepath)

    return sorted_filepaths

def prepare(filepath): #Resize the images since they are 200x200
    image_array = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    new_array = cv2.resize(image_array, (100, 100))
    return new_array

def start_machine_learning(ordered_images):
    """Passes individual images to be classified by machine learning model"""
    music_item_list = []
    CATEGORIES = []

    # for folder in os.listdir("/Users/nick-kater/Desktop/classes/"):
    for folder in os.listdir(Path.cwd().joinpath("classes").as_posix()):
        if folder == ".DS_Store":
           pass
        else:
            CATEGORIES.append(folder)

    for image in ordered_images:
        new_array = prepare(image)
        new_array = np.array(new_array).reshape(-1, 100, 100)

        # model = tf.keras.models.load_model('/Users/nick-kater/Desktop/working.model')
        model = tf.keras.models.load_model(Path.cwd().joinpath('working.model').as_posix())
        prediction = model.predict([new_array])
        p = np.argmax(prediction)

        output = CATEGORIES[p]
        individual_music_info = []

        individual_music_info.append(output)
        individual_music_info.append(image)
        music_item_list.append(individual_music_info)

    return music_item_list

def clean_up_bass_clef(music_list):
    """Helps clean up problems image processing has with bass clef symbol"""

    music_list[0][0] = "bass-clef"
    dot_count = 0
    symbols_to_be_removed = []
    while dot_count < 2:
        for music_index in range(len(music_list)):
            if dot_count == 2:
                break
            elif music_list[music_index][0] == 'bass-clef' and music_index == 0:
                dot_count = 0
            elif music_list[music_index][0] == 'dot' and music_index != 0:
                dot_count += 1
            else:
                symbols_to_be_removed.append(music_list[music_index])

    for symbol in symbols_to_be_removed:
        if symbol in music_list:
            music_list.remove(symbol)
        else:
            pass

    return music_list

def flat_or_sharp_pitch(music_list, line_coordinates, cntr_index_LtoR, contours):
    for index in range(len(music_list)):
        if "sharp" in music_list[index][0]:
            sharp_index = cntr_index_LtoR[index]
            sharp_contour = contours[sharp_index]
            M = cv2.moments(sharp_contour)
            cY = int(M["m01"] / M["m00"])
            #print("Sharp y-ave is {}".format(cY))

            if cY in line_coordinates:
                sharp_line_above = 0
                sharp_line_below = 0
                for line in line_coordinates:
                    if cY > line:
                        sharp_line_above += 1
                    elif cY < line:
                        sharp_line_below += 1
                    else:
                        continue

                if sharp_line_below == 4 and sharp_line_above == 0:
                    if music_list[0][0] == 'g-clef':
                        #print("F sharp")
                        note_to_modify = ['F', 'up']
                        return note_to_modify
                    elif music_list[0][0] == 'bass-clef':
                        #print("A sharp")
                        note_to_modify = ['A', 'up']
                        return note_to_modify
                if sharp_line_below == 3 and sharp_line_above == 1:
                    if music_list[0][0] == 'g-clef':
                        #print("D sharp")
                        note_to_modify = ['D', 'up']
                        return note_to_modify
                    elif music_list[0][0] == 'b-clef':
                        #print("F sharp")
                        note_to_modify = ['F', 'up']
                        return note_to_modify

        elif 'flat' in music_list[index][0]:
            flat_index = cntr_index_LtoR[index]
            flat_contour = contours[flat_index]
            M = cv2.moments(flat_contour)
            cY = int(M["m01"] / M["m00"])
            #print("Flat y -ave is {}".format(cY))
            flat_line_above = 0
            flat_line_below = 0

            for staff in line_coordinates:
                if cY-4 <= staff <= cY+4:
                    temp_compare.remove(staff)
                    for line in temp_compare:
                        if cY > line:
                            flat_line_above += 1
                        elif cY < line:
                            flat_line_below +=1
                        else:
                            continue
            if flat_line_below == 2 and flat_line_above == 2:
                #print("b flat")
                note_to_modify = ['B', 'down']
                return note_to_modify
            else:
                pass

    return None

def find_line_coordinates(line_contours):
    """finds coordinates of removed staff lines"""
    line_coords = []

    for line_index in range(len(line_contours)):
            c = line_contours[line_index]
            extBot = tuple(c[c[:, :, 1].argmax()][0])
            line_coords.append(extBot[1])

    return line_coords

def find_pitch_notes(music_list):
    pitch = []
    notes_to_classify = ["quarter", "half", "whole"]

    for music_item in music_list:
        if music_item[0] in notes_to_classify:
            pitch.append(music_item)

    return pitch

def find_pitch_location(pitch, cntr_index_LtoR):
    ordered_pitch = []

    for note in pitch:
        location = os.path.basename(os.path.normpath(note[1]))
        index = int(location.split(".")[0])
        ordered_pitch.append(cntr_index_LtoR[index])

    return ordered_pitch

def classify_pitch(ordered_pitch, music_list, image, line_coordinates, contours):
    notes_to_classify = ["quarter", "half", "whole"]

    pitches = []

    for pitch in ordered_pitch:
        dimensions  = image.shape #get dimensiions of original image
        x = dimensions[0] #Store x
        y = dimensions[1] #Store y
        im2 =  np.zeros((x,y,3), np.uint8)
        im3 = np.zeros((x,y,3), np.uint8)

        cv2.drawContours(im2, contours, pitch, (255,255,255), cv2.FILLED)

        gray = cv2.cvtColor(im2,cv2.COLOR_BGR2GRAY) #Convert to grayscale
        gray2 = cv2.cvtColor(im3,cv2.COLOR_BGR2GRAY) #Convert to grayscale

        bw = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1] #Convert to binary image
        bw2 = cv2.threshold(gray2, 150, 255, cv2.THRESH_BINARY_INV)[1] #Convert to binary image

        bw = ~bw
        bw2 = ~bw2

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8,8))
        dilation = cv2.dilate(bw,kernel,iterations = 1)
        circ = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        cv2.drawContours(bw2, circ, -1, (255,255,255), cv2.FILLED)

        c_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        opening = cv2.morphologyEx(bw2, cv2.MORPH_OPEN, c_kernel, iterations=3)
        circle_contours = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        M = cv2.moments(circle_contours[0])
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        line_above = 0
        line_below = 0

        if music_list[0][0] == "g-clef":
            if cY-1 in line_coordinates or cY in line_coordinates or cY+1 in line_coordinates:
                for line in line_coordinates:
                    if line - cY == 1 or cY - line ==1 or cY == line:
                        continue
                    elif cY - 1 > line or cY > line or cY+2 > line:
                        line_above +=1
                    elif cY < line and cY - 1 < line or cY+1 < line:
                        line_below +=1

                if line_above == 4 and line_below == 0:
                    #print('note is E4')
                    pitches.append('E4')
                elif line_above == 3 and line_below == 1:
                    #print('note is G4')
                    pitches.append('G4')
                elif line_above == 2 and line_below == 2:
                    #print('note is B4')
                    pitches.append('B4')
                elif line_above ==1 and line_below == 3:
                    #print('note is D5')
                    pitches.append('D5')
                elif line_above == 0 and line_below ==4:
                    #print('note is F5')
                    pitches.append('F5')

            else:
                if cY > max(line_coordinates) + 10:
                    #print(cY)
                    above_y = cY - max(line_coordinates)
                    if above_y % 17 == 0 or above_y % 18 == 0:
                        line_below = above_y // 17
                        if line_below == 1:
                            #print("note is C4")
                            pitches.append('C4')
                        elif line_below == 2:
                            #print("note is A3")
                            pitches.append('A3')
                    else:
                        if 2 < above_y - 17 < 15:
                            #print("note is B3")
                            pitches.append("B3")
                elif cY < min(line_coordinates) - 10:
                    above_y = min(line_coordinates) - cY
                    if above_y % 17 == 0 or above_y % 18 == 0:
                        line_above = above_y // 17
                        if line_above == 1:
                            #print("note is A5")
                            pitches.append("A5")
                    else:
                        if 15 > 17 - above_y > 2:
                            #print("note is B5")
                            pitches.append("B5")
                else:
                    for line in line_coordinates:
                        if cY > line:
                            line_above += 1
                        elif cY < line:
                            line_below +=1
                    if line_above == 5 and line_below == 0:
                        #print("note is D4")
                        pitches.append('D4')
                    elif line_above == 4 and line_below == 1:
                        #print("note is F4")
                        pitches.append('F4')
                    elif line_above == 3 and line_below == 2:
                        #print("note is A4")
                        pitches.append('A4')
                    elif line_above == 2 and line_below == 3:
                        #print("note is C5")
                        pitches.append('C5')
                    elif line_above == 1 and line_below == 4:
                        #print("note is E5")
                        pitches.append('E5')
                    elif line_above == 0 and line_below == 5:
                        #print("note is G5")
                        pitches.append('G5')

        else: #Line is bass-clef

            if cY-1 in line_coordinates or cY in line_coordinates or cY+1 in line_coordinates:
                for line in line_coordinates:
                    if line - cY == 1 or cY - line ==1 or cY == line:
                    #note is on this line
                        continue
                    elif cY - 1 > line or cY > line or cY+2 > line:
                        line_above +=1
                    elif cY < line and cY - 1 < line or cY+1 < line:
                        line_below +=1
                #print(line_above, line_below)

                if line_above == 4 and line_below == 0:
                    #print('note is G2')
                    pitches.append('G2')
                elif line_above == 3 and line_below == 1:
                    #print('note is B2')
                    pitches.append('B2')
                elif line_above == 2 and line_below == 2:
                    #print('note is D3')
                    pitches.append('D3')
                elif line_above ==1 and line_below == 3:
                    #print('note is F3')
                    pitches.append('F3')
                elif line_above == 0 and line_below ==4:
                    #print('note is A3')
                    pitches.append('A3')

            else:
                if cY > max(line_coordinates) + 10:
                    #print(cY)
                    above_y = cY - max(line_coordinates)
                    if above_y % 17 or above_y % 18 == 0:
                        line_below = above_y // 17
                        if line_below == 1:
                            #print("note is E2")
                            pitches.append('E2')
                        elif line_below == 2:
                            #print("note is C2")
                            pitches.append('A3')
                    else:
                        if 2 < above_y - 17 < 15:
                            #print("note is D2")
                            pitches.append("D2")
                elif cY < min(line_coordinates) - 10:
                    above_y = min(line_coordinates) - cY
                    if above_y % 17 == 0 or above_y % 18 == 0:
                        line_above = above_y // 17
                        if line_above == 1:
                            #print("note is C4")
                            pitches.append("C4")
                    else:
                        if 15 > 17 - above_y > 2:
                            #print("note is D4")
                            pitches.append("D4")
                else:
                    for line in line_coordinates:
                        if cY > line:
                            line_above += 1
                        elif cY < line:
                            line_below +=1
                    if line_above == 5 and line_below == 0:
                        #print("note is F2")
                        pitches.append('F2')
                    elif line_above == 4 and line_below == 1:
                        #print("note is A2")
                        pitches.append('A2')
                    elif line_above == 3 and line_below == 2:
                        #print("note is C3")
                        pitches.append('C3')
                    elif line_above == 2 and line_below == 3:
                        #print("note is E3")
                        pitches.append('E3')
                    elif line_above == 1 and line_below == 4:
                        #print("note is G3")
                            pitches.append('G3')
                    elif line_above == 0 and line_below == 5:
                        #print("note is B3")
                        pitches.append('B3')

    pitch_count = 0

    for index in range(len(music_list)):

        if music_list[index][0] in notes_to_classify:
            music_list[index].append(pitches[pitch_count])
            pitch_count += 1
        else:
            pass

    return music_list

def apply_flat_or_sharp(note_to_modify, music_list):
    if note_to_modify != None:
        for music_item in music_list:
            if len(music_item) == 3:
                if note_to_modify[0] in music_item[2]:
                    pitch_mod = all_notes.index(music_item[2])
                    if note_to_modify[1] == "up":
                        music_item[2] = all_notes[pitch_mod + 1]
                    elif note_to_modify[1] == "down":
                        music_item[2] = all_notes[pitch_mod - 1]
                else:
                    pass
            else:
                pass

        return music_list

    else:
        return music_list

def clean_up_half_notes(music_list):
    for index in range(len(music_list)):
        if music_list[index][0] == "line" and (index != len(music_list) and index != len(music_list)-1):
            if music_list[index+1][0] == "quarter" and music_list[index+2][0] == "quarter" and music_list[index+3][0] == "line":
                music_list[index+1][0] = "half"
                music_list[index+2][0] = "half"
            elif music_list[index+1][0] == "bar-rest" and music_list[index+2][0] == "quarter" and music_list[index+3] == "line":
                music_list[index+2][0] = "half"
            elif music_list[index+1] == "quarter" and music_list[index+2][0] == "bar-rest" and music_list[index+3][0] == "line":
                music_list[index+1][0] = "half"
            elif music_list[index+1][0] == "quarter" and music_list[index+2][0] == "half" and music_list[index+3][0] == "line":
                music_list[index+1][0] = "half"
            elif music_list[index+1][0] == "half" and music_list[index+2][0] == "quarter" and music_list[index+3][0] == "line":
                music_list[index+2][0] = "half"
            else:
                pass
        elif music_list[index][0] == "g-clef" or music_list[index][0] == "bass-clef":
            if music_list[index+1][0] == "quarter" and music_list[index+2][0] == "quarter" and music_list[index+3][0] == "line":
                music_list[index+1][0] = "half"
                music_list[index+2][0] = "half"
        else:
            pass

    return music_list

def convert_classification_to_text(music_list):
    """Based on classification and pitch write to a file to be sent to hardware"""

    output_string = ""
    for music_index in range(len(music_list)):
        if music_list[music_index][0] == "g-clef":
            output_string = output_string + "R 100 "
        if music_list[music_index][0] == "bass-clef":
            output_string = output_string + "L 100 "
        elif music_list[music_index][0] == "4/4":
            output_string = output_string + "4/4 "
        elif music_list[music_index][0] == "quarter":
            output_string = output_string + "4/{} ".format(music_list[music_index][2])
        elif music_list[music_index][0] == "half":
            output_string = output_string + "2/{} ".format(music_list[music_index][2])
        elif music_list[music_index][0] == "whole":
            output_string = output_string + "1/{} ".format(music_list[music_index][2])
        elif music_list[music_index][0] == "bar-rest":
            if music_list[music_index-1][0] == "line" and music_list[music_index+1][0] == "line":
                output_string = output_string + "1/R "
            elif music_list[music_index-1][0] == "4/4" and music_list[music_index+1][0] == "line":
                output_string = output_string + "1/R "
            elif music_list[music_index-1][0] == "g-clef" and music_list[music_index+1][0] == "line":
                output_string = output_string + "1/R "
            elif music_list[music_index-1][0] == "bass-clef" and music_list[music_index][0] == "line":
                output_string = output_string + "1/R "
            else:
                output_string = output_string + "2/R "
        elif music_list[music_index][0] == "quarter-rest":
            output_string = output_string + "4/R "

    return output_string

def clean_up_folder(folder_path):
    """Remove the individual images from the placeholder folder"""
    for file in os.listdir(folder_path):
        file_to_remove = os.path.join(folder_path, file)
        os.remove(file_to_remove)

def find_music_to_read():
    folder_to_watch = "/Users/nick-kater/Documents/pianists_OMR/watch_folder"

    for file in os.listdir(folder_to_watch):
        if file.endswith(".json"):
            print(os.path.join("/Users/nick-kater/Documents/pianists_OMR/watch_folder", file))
            with open(os.path.join("/Users/nick-kater/Documents/pianists_OMR/watch_folder", file)) as f:
                files = json.load(f)

            name = files["pdf"]
            name = os.path.split(name)[1]
            name = os.path.splitext(name)[0]
            return name
        else:
            pass

def load_images(name):
    music_folder = "/Users/nick-kater/Documents/pianists_OMR/songs"
    for music in os.listdir(music_folder):
        if name in music:
            return os.path.join(music_folder, music)
        else:
            pass


# raw_images = Path.cwd().joinpath("line_crop")
# image = cv2.imread(raw_images.joinpath('1_0.png').as_posix())

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("img")
    args = ap.parse_args()

    print(args.img)
    image = cv2.imread(Path(args.img).as_posix())

bw = binary_convert(image)
no_line, line_contours = line_detect_and_remove(image, bw)
binary_no_line_invert = binary_convert(no_line)
contours = extract_contours(binary_no_line_invert)
cntr_index_LtoR = extract_individual_image(image, ~no_line, contours)

cropped_images = Path.cwd().joinpath("cropped")
#ordered_files = order_sort("/Users/nick-kater/Desktop/feeding")
ordered_files = order_sort(cropped_images)
music_item_list = start_machine_learning(ordered_files)
music_item_list = clean_up_bass_clef(music_item_list)
print(music_item_list)

line_coordinates = find_line_coordinates(line_contours)
pitch = find_pitch_notes(music_item_list)
print(pitch)

ordered_pitch = find_pitch_location(pitch, cntr_index_LtoR)
print(music_item_list)

music_item_list = classify_pitch(ordered_pitch, music_item_list, image, line_coordinates, contours)
note_to_modify = flat_or_sharp_pitch(music_item_list, line_coordinates, cntr_index_LtoR, contours)
music_item_list = apply_flat_or_sharp(note_to_modify, music_item_list)
music_item_list = clean_up_half_notes(music_item_list)
text_output = convert_classification_to_text(music_item_list)
print(text_output)

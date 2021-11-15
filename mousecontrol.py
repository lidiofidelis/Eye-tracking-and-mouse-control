"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2, dlib
import pyautogui, sys
from gaze_tracking import GazeTracking
import math
import numpy as np
import simpleaudio as sa

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
mirror = True
x_ds, x_es, x_di, x_ei = 0,0,0,0                # Mapeamento do x
y_ds, y_es, y_di, y_ei = 0,0,0,0                # Mapeamneto do y
x_ds1, x_es1, x_di1, x_ei1 = 0,0,0,0       
y_ds1, y_es1, y_di1, y_ei1 = 0,0,0,0 
count, estado, counti = 0,0,0
tempo = 50
cte = []
cte1 = []
# Áudio para o Click
frequency = 440
fs = 44100
seconds = 3 
t = np.linspace(0, seconds, seconds * fs, False)
note = np.sin(frequency * t * 2 * np.pi)
audio = note * (2**15 - 1) / np.max(np.abs(note))
audio = audio.astype(np.int16)
# Calibração
while count < tempo * 4.5:
    _, frame = webcam.read()
    if mirror:
        frame = cv2.flip(frame,1)
    frame = frame.copy()
    gaze.refresh(frame[100:350, 200:450])
    frame = gaze.annotated_frame()
    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    if left_pupil != None:
        if estado == 0:
            print("Preparando")
            count+=1
            if count == 7:
                estado+=1
        elif estado == 1:
            if counti == 0:
                print("Olhe para o canto superior esquerdo da tela")
            x_es = left_pupil[0]
            y_es = left_pupil[1]
            count+=1
            counti+=1
            if count == 1.5 * tempo:
                estado+=1
                counti = 0
        elif estado == 2:
            if counti == 0:
                print("Olhe para o canto inferior esquerdo da tela!")
            x_ei = left_pupil[0]
            y_ei = left_pupil[1]
            count+=1
            counti+=1
            if count == 2.5 * tempo:
                estado+=1
                counti = 0
        elif estado == 3:
            if counti == 0:
                print("Olhe para o canto inferior direito da tela!")
            x_di = left_pupil[0]
            y_di = left_pupil[1]
            count+=1
            counti+=1
            if count == 3.5 * tempo:
                estado+=1
                counti = 0
        else:
            if counti == 0:
                print("Olhe para o canto superior direito da tela!")
            x_ds = left_pupil[0]
            y_ds = left_pupil[1]
            count+=1
            counti+=1
            if count == 4.5 * tempo:
                break
x_to = x_es if x_ei>x_es else x_ei
x_tf = x_di if x_di>x_ei else x_ei
y_to = y_es if y_ds>y_es else y_ds
y_tf = y_di if y_di>y_ei else y_ei
count, counti = 0, 0
N = 20
v = []
v2 = []
aux = []
aux1 = []
xmed,aux_med,aux_med1,ymed = 0, 0, 0, 0
# Mapeamento 
while True:
    pyautogui.FAILSAFE = False
    resolution = pyautogui.size()
    _, frame = webcam.read()
    if mirror:
        frame = cv2.flip(frame,1)
    frame = frame.copy()
    gaze.refresh(frame[100:350, 200:450])
    frame = gaze.annotated_frame()
    left_pupil = gaze.pupil_left_coords()
    if left_pupil != None:
        aux = [left_pupil[0]] + aux[:N-1]
        aux1 = [left_pupil[1]] + aux1[:N-1]
        frame = gaze.annotated_frame()
    if len(aux) == N and len(aux1) == N: 
        aux_med = sum(aux)/len(aux)
        aux_med1 = sum(aux1)/len(aux1)
    if left_pupil != None:      
        x_p = math.fmod(int((resolution[0]/(x_tf - x_to))*(aux_med - x_to)), resolution[0]+600)
        y_p = math.fmod(int((resolution[1]/(y_tf - y_to))*(aux_med1 - y_to)), resolution[1]+400)
        if x_p >= resolution[0]:
            x_p = resolution[0]-10
        elif y_p >= resolution[1]:
            y_p = resolution[1]-10
        elif x_p <= 0:
            x_p = 10
        elif y_p <= 0:
            y_p = 10
        v = [x_p] + v[:N-1]
        v2 = [y_p] + v2[:N-1]  
    if len(v2) == N and len(v) == N: 
        frame = gaze.annotated_frame()  
        ymed = sum(v2)/len(v2)
        xmed = sum(v)/len(v)
        v.clear()
        v2.clear()
        aux.clear()
        aux1.clear() 	
        pyautogui.moveTo(xmed,ymed)
    if left_pupil == None:
        pyautogui.moveTo(None,None)
# Click direito do Mouse
    if gaze.is_blinking(): 
        pyautogui.moveTo(None,None)
        counti +=1
        if counti == 20:
            pyautogui.click(None,None)
            play_obj = sa.play_buffer(audio, 1, 2, fs)
            counti = 0
    cv2.imshow("EYE", frame)
    if cv2.waitKey(1) == 27:
        break

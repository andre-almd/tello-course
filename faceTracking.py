#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 13:42:04 2021

@author: andre-itv
"""

import cv2
import numpy as np
from djitellopy import tello
from time import sleep

# Create the tello object
me = tello.Tello()

me.connect()
print(f'Bateia: {me.get_battery()}')

me.streamon()

# Inicia o voo e e sobe com velocidade 25 por 8s
me.takeoff()
sleep(2)
me.send_rc_control(0, 0, 25, 0)
sleep(8)
me.send_rc_control(0, 0, 0, 0)


# Variáveis para controle
# 
#  
w, h = 360, 240

fbRange = [6200, 6800]

# Parametros de pid
pid = [0.4, 0.4, 0]
pError =  0

# Função para encontrar a face e mapear a área e o centro
def findFace(img):
    
    # Cascade para encontrar face
    faceCascade = cv2.CascadeClassifier('Resources/haarcascades/haarcascade_frontalface_default.xml')
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detecta faces
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)
    
    # Listas para informações das faces detectadas
    myFaceListC = []
    myFaceListArea = []
    
    # loop para varrer todos as faces
    for (x,y,w,h) in faces:
        
        # Desenha retangulo
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
        
        # Calcula ponto central
        cx = x + w // 2
        cy = y + h // 2
        
        # Calcula area
        area = w * h
        
        # Desenha circulo no ponto central
        cv2.circle(img, (cx,cy), 5, (0,255,0), cv2.FILLED)
        
        # Adiciona dados nas listas
        myFaceListC.append([cx, cy])
        myFaceListArea.append(area)
        
    # Se detectar alguma face identifica e retorna a mais próxima pela aera
    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img, [[0,0], 0]
    
# Funcao para o drone seguir a face    
def trackface(me, info, w, pid, pError):
    
    global fbRange
    
    x, y = info[0]
    area = info[1]
    
    # forward backward
    fb = 0
    
    # Erro em x
    error = x - w//2
    
    speed = pid[0]*error + pid[1]*(error-pError)
    speed = int(np.clip(speed, -100, 100))
    
    # Define o comando de voo fb para o drone em funcao da area
    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb = -20
    elif area < fbRange[0] and area != 0:
        fb = 20
        
    if x == 0:
        speed = 0
        error = 0
    
    me.send_rc_control(0, fb, 0, speed)
    
    return error
    
    
    
#cap = cv2.VideoCapture(4)

while True:
    #_, img = cap.read()
    img = me.get_frame_read().frame
    
    img = cv2.resize(img, (w,h))
    
    # Encontra face
    img, info = findFace(img)
    
    # Movimenta drone de acordo informacoes de posicao da face
    pError = trackface(me, info, w, pid, pError)
    
    #print('Center: ', info[0], '; Area: ', info[1])
    
    cv2.imshow('Output', img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break
    
cv2.destroyAllWindows()
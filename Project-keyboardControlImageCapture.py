#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 20:19:37 2021

@author: andre-itv
"""

import keyPressModule as kp

from djitellopy import tello
import time
import cv2

# Inicia o módulo de capturar o teclado com pygame
kp.init()

# Cria o objeto tello paracontrolar o drone
me = tello.Tello()

# Conecta com o drone e checa nível de bateria
me.connect()
print(f'Battery: {me.get_battery()}')

# Cria a variável para salvar as imagens
global img

# Inicia o steam da câmera
me.streamon()


# Função para realizar os comandos de voo
def getKeyboardInput():
    
    # lr: left - rigth
    # fb: forward - backward
    # ud: up - down
    # yv: yaw velocity
    
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50
    
    # Captura dos movimentos
    if kp.getKey('LEFT'):
        lr = -speed
    elif kp.getKey('RIGHT'):
        lr = speed
        
    if kp.getKey('UP'):
        fb = speed
    elif kp.getKey('DOWN'):
        fb = -speed
        
    if kp.getKey('w'):
        ud = speed
    elif kp.getKey('s'):
        ud = -speed
        
    if kp.getKey('a'):
        yv = -speed
    elif kp.getKey('d'):
        yv = speed
        
    # Captura das teclas de takeoff e land
    if kp.getKey('e'):
        me.takeoff()
        
    if kp.getKey('q'):
        me.land()
        
    # Captura da tecla de salvar foto
    if kp.getKey('z'):
        cv2.imwrite(f'Resources/Images/{time.time()}.jpg', img)
        time.sleep(0.3)
        
    return [lr, fb, ud, yv]


while True:
    
    # Captura as teclas
    vals = getKeyboardInput()
    
    # Envia comandos de voo parao drone
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    
    # Captra o frame
    img = me.get_frame_read().frame
    #img = cv2.resize(img, (360, 240))
    
    cv2.imshow('image from Drone', img)
        
    c = cv2.waitKey(1)
    if c == 27:
        me.land()
        time.sleep(2)
        break
    
cv2.destroyAllWindows()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 13:32:07 2021

@author: andre-itv
"""

import keyPressModule as kp
from djitellopy import tello
from time import sleep
import numpy as np
import cv2
import math


# #################################### PARAMETERS ########################################
# Baseados nas informações do curso (O tello não é muito preciso, pode variar em cada drone. 
                                                #               Precisa de testes de cada drone para ter certeza)
fSpeed = 117/10 # Forward speed in cm/s (15cm/s)
aSpeed = 360/10 # Angular speed Degrees/s (50 cm/s)
interval = 0.25


# Distância percorrida por intervalo para mapeamento
dInterval = fSpeed * interval
aInterval = aSpeed * interval

# #####################################################################################

x, y = 500, 500
ang = 0
yaw = 0

kp.init()
me = tello.Tello()

me.connect()
print(me.get_battery())

points = []

def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 15
    aSpeed = 50
    
    dist = 0
    global ang
    global yaw
    global x
    global y
    
    if kp.getKey('LEFT'):
        lr = -speed
        dist = dInterval
        ang = -180
    elif kp.getKey('RIGHT'):
        lr = speed
        dist = -dInterval
        ang = 180
        
    if kp.getKey('UP'):
        fb = speed
        dist = dInterval
        ang = 270
    elif kp.getKey('DOWN'):
        fb = -speed
        dist = -dInterval
        ang = -90
        
    if kp.getKey('w'):
        ud = speed
    elif kp.getKey('s'):
        ud = -speed
        
    if kp.getKey('a'):
        yv = -aSpeed
        yaw -= aInterval
    elif kp.getKey('d'):
        yv = aSpeed
        yaw += aInterval
        
    if kp.getKey('e'):
        me.takeoff()
        
    if kp.getKey('q'):
        me.land()
        
    sleep(interval)
    
    ang += yaw
    x += int(dist * math.cos(math.radians(ang)))
    y += int(dist * math.sin(math.radians(ang)))
        
    return [lr, fb, ud, yv, x, y]


def drawPoints(img, points):
    for point in points:
        cv2.circle(img, (point), 10, (0, 0, 255), cv2.FILLED)
    cv2.circle(img, points[-1], 15, (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'({(points[-1][0]-500)/100} , {(points[-1][1]-500)/100})m', (points[-1][0]+10, points[-1][0]+30), 
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)

while True:
    vals = getKeyboardInput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    
    
    img = np.zeros((1000, 1000, 3), np.uint8)
    
    points.append((vals[4], vals[5]))
    drawPoints(img, points)
    
    cv2.imshow('Output', img)
    cv2.waitKey(1)
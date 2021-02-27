#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 19:59:30 2021

@author: andre-itv
"""

import keyPressModule as kp
from djitellopy import tello
from time import sleep


kp.init()
me = tello.Tello()

me.connect()
print(me.get_battery())

def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50
    
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
        
    if kp.getKey('e'):
        me.takeoff()
        
    if kp.getKey('q'):
        me.land()
        
    return [lr, fb, ud, yv]


while True:
    vals = getKeyboardInput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)
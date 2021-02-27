#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 19:22:37 2021

@author: andre-itv
"""

from djitellopy import tello
from time import sleep
import cv2

# Create the tello object
me = tello.Tello()

me.connect()

print(f'Bateia: {me.get_battery()}')

me.streamon()

while True:
        img = me.get_frame_read().frame
        img = cv2.resize(img, (360, 240))
        cv2.imshow('image from Drone', img)
        
        cv2.waitKey(1)
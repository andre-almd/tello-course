#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 18:54:59 2021

@author: andre-itv
"""

from djitellopy import tello
from time import sleep

# Create the tello object
me = tello.Tello()

me.connect()


print(f'Bateia: {me.get_battery()}')

me.takeoff()
 
me.send_rc_control(left_right_velocity = 0, forward_backward_velocity = 0, up_down_velocity = 0, yaw_velocity = 100)
sleep(1)
me.send_rc_control(0, 0, 0, 0)
me.land()

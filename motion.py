# !/usr/bin/env python
# This program balances an inverted pendulum on top of a driveable robot.
# The program is based on Peiyue Zhao's program, that is based on the following resources:
#------------------------------------------------------------------------------------------------------
# https://www.dexterindustries.com/BrickPi/
# https://github.com/DexterInd/BrickPi3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/BrickPi3/blob/master/LICENSE.md
#
#-------------------------------------------------------------------------------------------------------
#  http://www.nxtprograms.com/NXT2/segway/
#-------------------------------------------------------------------------------------------------------
#  https://www.youtube.com/watch?v=35rLMKCqGZM
# ------------------------------------------------------------------------------------------------------
#  Hardware:
#     Connect an EV3 infrared sensor to BrickPi3 sensor port 1.
#     Connect the top motor to BrickPi3 motor port B.
#     Connect the left motor to BrickPi3 motor port A.
#     Connect the right motor to BrickPi3 motor port D.
#     Set EV3 infrared remote to channel 1.
# 	  Connect EV3 Sensor to Sensor Port 1

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                          

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers
import sys      # import sys for sys.exit()
import os
import json     # import file handling suitable for network transmission
import socket   # import network communication package
import select

 


# Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
BP = brickpi3.BrickPi3() 

# define which ports the sensors and motors are connected to.
PORT_SENSOR_IR   = BP.PORT_1
PORT_MOTOR_TOP   = BP.PORT_B
PORT_MOTOR_LEFT  = BP.PORT_A
PORT_MOTOR_RIGHT = BP.PORT_D
BP.reset_all()

def motion(listener):#

    power_value = 0

     
    print('check1')	 
    power_input = listener.recv(1024)                         #Receive data from GUI
    print('check2')
    power_input = json.loads(power_input.decode('utf-8'))            #Unpack data from GUI
    power_value = power_input["PowerValue"]
	
    print(power_value)
    return power_value

while True:

     UDP_IP = '192.168.10.11' # it was 0.0.0.0 (RPi's IP)
     UDP_PORT_GUI = 32152

     GUI_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     GUI_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
     GUI_listener.bind((UDP_IP, UDP_PORT_GUI))
  
                            
     # reset the encoders
     BP.reset_motor_encoder(PORT_MOTOR_TOP)
     BP.reset_motor_encoder(PORT_MOTOR_LEFT)
     BP.reset_motor_encoder(PORT_MOTOR_RIGHT)

     rightRef = 0
     leftRef = 0
     turnRight = False
     turnLeft = False

     # get the current time in ms
     CurrentTick = int(round(time.time() * 1000))
        
     tMotorPosOK = CurrentTick
     #tCalcStart = CurrentTick - LOOP_TIME
     NextBalanceTime = CurrentTick
     leftPower = 0
     rightPower = 0

     d = 0.042 # Diameter of wheel
     d2r = 0.0175 # Degrees to radians
     V2P = 100/9 # Volt to power (where power means input to motor)
     TimeOffset = 0
     MaxVolt=9
     MaxPower=100
     command = 3
     print("Balancing and steering activated.")
        
     while True:
            power_value = motion(GUI_listener)

            leftPower = power_value
            rightPower= power_value

            BP.set_motor_power(PORT_MOTOR_LEFT , -leftPower)
            BP.set_motor_power(PORT_MOTOR_RIGHT, -rightPower) 
                



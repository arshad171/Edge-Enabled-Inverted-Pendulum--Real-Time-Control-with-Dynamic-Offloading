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

LOOP_SPEED = 120
# how fast to run the balance loop in Hz. Slower is less CPU intensive, but faster helps the balance bot to work better. Realistically anything over 120 doesn't make a difference.

KCORRECTTIME = 0.001   # a constant used to correct the delay to try to maintain a perfect loop speed (defined by LOOP_SPEED)

# Change to angular fall limit? If abs(get_motor_encoder) > 90, assume pendulum has fallen and quit?
ANGLE_FALL_LIMIT = 70 # If top motor's angular sensor measures more than +/- 85 degrees, assume the pendulum fell over assume that the robot fell.

LOOP_TIME = (1 / LOOP_SPEED)        # how many seconds each loop should take (at 100 Hz, this should be 0.01)

# call this function to turn off the motors and exit safely.
def SafeExit():
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
    sys.exit()

def SafeExitAndClose():
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
    os.system('shutdown -s')    

def findPendControlInput(pendError):
    # Sends measured error of pendulum in rads, recieves pendulum input in volts

    # Format measurement to send to controller
    measurement = {"pendError": pendError}
    measurement = json.dumps(measurement).encode('utf-8') # Convert it to bytes format, expected from socket

    # Create a socket (TCP/IP)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Open socket with timeout = sampling time and correct server address
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #server_address = ('127.0.0.1',32149) # Change to your server's address
    server_address = ('192.168.10.219', 32149) # The PID controller IP (Edge Server)
    #server_address = ('192.168.10.11', 32149) # The PID controller IP (Local control)
    client.settimeout(2) # How long the client waits (0.1)
    try:
    	client.sendto(measurement, server_address)
    	#print("Measurement sent to server: " + str(server_address))
        output, server = client.recvfrom(4096)
        print("Recieved control signal")
        output=json.loads(output.decode('utf-8'))
        print("CtrSig: " + str(output))
        client.close()
        success=1
        return output["F"], success
    except:
        print("No signal received")
        success=0
        return 0, success

def driveFeedback(pos, ref, A, B, K, obs, LIMIT):
    # Calculates (and eventually saturates) motor input from reference signal, measured position, observers and 1x2 gain vector K
    # and updates vehicle observer according to values of 2x3 matrix A & 1x2 vector B

    u = K[0]*(ref-pos) + K[1]*obs[1]
    if u > LIMIT:
        u = LIMIT
    elif u < -LIMIT:
        u = -LIMIT
    obs_0_old = obs[0]
    obs[0] = A[0][0]*pos + A[0][1]*obs_0_old + A[0][2]*obs[1] + B[0]*u
    obs[1] = A[1][0]*pos + A[1][1]*obs_0_old + A[1][2]*obs[1] + B[1]*u
    motorInput = u*100/9 # Convert to motor power input
    return motorInput, obs

def start_pendulum_control(listener):

    command = 7
 
    direction = listener.recv(1024)                              #Receive data from GUI
    direction = json.loads(direction.decode('utf-8'))            #Unpack data from GUI
    if direction["pendulum_control_signal"]==1:  # Steady state calibrated
       command = 1
   
    return command

def stop_pendulum_control(listener):

    command = 7
    
    ready = select.select([listener], [], [], 0)
    if ready[0]:
       direction = listener.recv(1024)                              #Receive data from GUI
       direction = json.loads(direction.decode('utf-8'))            #Unpack data from GUI
       if direction["pendulum_control_signal"]==4:  # Steady state calibrated
          command = 4
   
    return command

print("Make sure the pendulum is upright. Then press Confirm stedy state button in GUI.")
    
while True:

     UDP_IP = '192.168.10.11' # RPi's IP
     UDP_PORT_GUI = 32151

     GUI_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     GUI_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
     GUI_listener.bind((UDP_IP, UDP_PORT_GUI))

        
     command_start = start_pendulum_control(GUI_listener)

     if command_start == 1:
	# this corresponds to pressing confirm steady state
                            
        # reset the encoders
        BP.reset_motor_encoder(PORT_MOTOR_TOP)

        try:
            # Assuming the motor is connected to port B
            motor_port = BP.PORT_B

            # Set the motor power to make it move
            BP.set_motor_power(motor_port, 30)  # Adjust power as needed

            # Wait for the motor to reach the desired angle
            desired_angle = 90  # Adjust the angle as needed
            while True:
                current_angle = BP.get_motor_encoder(motor_port)
                print(f"Current Angle: {current_angle} degrees")

                if abs(current_angle) >= desired_angle:
                    # Stop the motor when the desired angle is reached
                    BP.set_motor_power(motor_port, 0)
                    break

                time.sleep(0.1)  # Adjust the sleep duration as needed

        finally:
            BP.reset_all()    
        # Save starting angle in radians, initialise updateable references and turning signals for wheels
        PendError = -BP.get_motor_encoder(PORT_MOTOR_TOP)
        PendError = PendError*0.0175 # Convert to radians
        PendPower = 0
        NewPower = 0
        
        print(f"PendError = {PendError}")
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
        
        LastTime = time.time() - LOOP_TIME
        TimeOffset = 0
        tInterval = LOOP_TIME
        MaxVolt= 9
        MaxPower= 100
        command = 3
        print("Balancing and steering activated.")
        
        
        while command_start:

            # loop at exactly the speed specified by LOOP_SPEED, and set tInterval to the actual loop time
            CurrentTime = time.time()
            TimeOffset += ((tInterval - LOOP_TIME) * KCORRECTTIME) # use this to adjust for any overheads, so that it tries to loop at exactly the speed specified by LOOP_SPEED
            DelayTime = (LOOP_TIME - (CurrentTime - LastTime)) - TimeOffset
            if DelayTime > 0:
               time.sleep(DelayTime)
            CurrentTime = time.time()
            tInterval = (CurrentTime - LastTime)
            LastTime = CurrentTime
            
 
		
            # Minus since theta and power has the same direction in motor sensor but different directions in the model
            PendError=-BP.get_motor_encoder(PORT_MOTOR_TOP)
            PendError=PendError*d2r
            NewPower, success = findPendControlInput(PendError)

            
            # If new signal was recieved, used this as input, otherwise keep the old input
            if success:
                PendPower = NewPower
            else:
                PendPower = PendPower
                  
            # Minus for left and right powers because driving motors are mounted invertedly

            BP.set_motor_power(PORT_MOTOR_TOP, PendPower)		
            #print(PendPower)
                
            if abs(BP.get_motor_encoder(PORT_MOTOR_TOP)) > ANGLE_FALL_LIMIT: # To keep the pendulum arm from oscillating out of controll
               print("Oh no! Pendulum fell. Exiting.")
               BP.reset_all()
               print("\n\nRestarting... Press safe exit to quit.\n\n")
               print("Make sure the pendulum is upright. Then press Confirm stedy state button in GUI.")
               mand_start = start_pendulum_control(GUI_listener)
               break

 
            command_stop = stop_pendulum_control(GUI_listener)

            if command_stop==4:
                print("Pendulum control stopped. Exiting.")
                BP.reset_all()
                print("Make sure the pendulum is upright. Then press Confirm stedy state button in GUI.")
                command_start = start_pendulum_control(GUI_listener)
                break


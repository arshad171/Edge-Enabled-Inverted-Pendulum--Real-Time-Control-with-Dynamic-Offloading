# Adam Miksits July 2019
# Edited by Jezdimir January 2020

from appJar import gui
import threading
import socket
import json
from tx import *
import time

global packet_counter  

packet_counter = 0
# Settings will include an option 0, 1, 2 or 3 - if option isn't 0 a "Value" is added to associate a quantity to option
settings  = {"Option": 0}                      # Set a default option for settings
start     = {"Start": 0}                       # Set a default option for start

direction = {"pendulum_control_signal": 0}           

# Set appropriate addresses (currently everything is sent to raspberry pi)
#server_address1  = ('192.168.60.4', 32150)   # IP of PID controller (local control)
server_address1 = ('192.168.40.11', 32150)  # IP of PID controller  (Edge Server)O
#server_address1  = ('192.168.20.11', 32150)   # IP of PID controller  (Local computing)
server_address2 = ('192.168.40.10', 32151)  # IP of Robot RPi
server_address3 = ('192.168.60.219', 32152)  # ('192.168.60.1', 32152)


# Next three lines make Client1 (Controller.py)
client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         # socket.AF_INET - internet  socket.SOCK_DGRAM - UDP (I guess send a UDP message over internet)
client1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      # Adjusting some options... 
client1.settimeout(11)                                             # Timeout so it does not get stuck, not necessary.

 
# Next three lines make Client 2 (pendulumcontroll.py)  
client2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         # socket.AF_INET - internet  socket.SOCK_DGRAM - UDP (I guess send a UDP message over internet)
client2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      # Adjusting some options... 
client2.settimeout(11)                                             # Timeout so it does not get stuck, not necessary.

# Next three lines make Client 3 (motioncontroll.py)  
client3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         # socket.AF_INET - internet  socket.SOCK_DGRAM - UDP (I guess send a UDP message over internet)
client3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      # Adjusting some options... 
client3.settimeout(11)          
thredcounter=0

def save_opt(button):
    # If any radio button is checked, set option to that, and value to the entry (unless normal op. is specified)
    global server_address
    global settings
    if button == "Save settings":
        addr = app.getEntry("Controller IP:")
        if addr:
            addr = addr.split(":")
            server_address = (addr[0], int(addr[1]))
        option = app.getRadioButton("Option")
        value = app.getEntry("Value:")
        if option == "Packet Loss":
            settings = {"Option": 1, "Value": value}
        elif option == "Transmission Loss":
            settings = {"Option": 2, "Value": value}
        elif option == "Delay":
            settings = {"Option": 3, "Value": value}
        elif option == "Normal operation":
            settings = {"Option": 0}
    elif button == "Reset":
        app.setRadioButton("Option", "Normal operation")
        app.setEntry("Value", 0)
        settings = {"Option": 0}
        
# Starts/stops controller, changes status bar accordingly if a response from the controller is received.
def start_stop(button):
    global start   # This global variable is used to start a controller
    try:
        if button == "Stop":
            start = {"Start": 0}                                               # Set start to 0
            client1.sendto(json.dumps(start).encode('utf-8'), server_address1) # Encode start and send it to server_address
            stopped = client1.recv(1024)                                       # Receive a message from client1
            stopped = json.loads(stopped.decode('utf-8'))                      # Decode a message
            if stopped["Stopped"]:                                             # If the message contains Stopped
                app.setLabel("Status", "Stopped")                              # Set status to stopped
                app.setLabelBg("Status", "red")                                
                app.setLabelBg("title", "red") 
        elif button == "Start":                                                # If button is start
            start = {"Start": 1}                                               # Set start to 1
            # message = {"Initialise": start, "Settings": settings}          
            message = json.dumps(start).encode('utf-8')                        # Encode start
            client1.sendto(message, server_address1)                           # Send start to client 1
            message2 = json.dumps(settings).encode('utf-8')                    # Encode settings
            client1.sendto(message2, server_address1)                           # Send settings to client 1
            start = client1.recv(1024)                                         # Recieve a message from the client1 and verify the connection is established 
            print()
            if start.decode('utf-8'):
                app.setLabel("Status", "Started")
                app.setLabelBg("Status", "green")
                app.setLabelBg("title", "green")
    except socket.timeout:
        pass

# Signalizes that the steady state is set
def pendulum_control(button):
     global direction_scale    
     try:
       if button == "Confirm steady state":
          pendulum_control_signal = {"pendulum_control_signal": 1}                             # Confirm steady state
          client2.sendto(json.dumps(pendulum_control_signal).encode('utf-8'), server_address2) # Encode and send  to server_address
        #   client3.sendto(message, server_address3) 
       elif button == "Safe exit":                                               # If button is Safe exit
          pendulum_control_signal = {"pendulum_control_signal": 4}                                           
          message = json.dumps(pendulum_control_signal).encode('utf-8')                        # Encode direction  
          client2.sendto(message, server_address2)                               # Send direction to client 2
     except socket.timeout:
        pass
def motion_thread_manage():
    global t1
    global thredcounter
    thredcounter=thredcounter+1
    powervalue = app.getScale("Power")
    Validity_Period = app.getEntry("Validity Period [ms]:")
    Interval=int(app.getEntry(" Interval: "))/1000.0
    t1 = threading.Thread(target=motion_control,args=(powervalue,Validity_Period,Interval))
    t1.start()

 # Moving the robot forward and backward
def motion_control(powervalue,Validity_Period,Interval):
    global packet_counter,thredcounter
    mythredcounter=thredcounter
    while mythredcounter==thredcounter:
        packet_counter = packet_counter + 1
        tx('d',packet_counter,powervalue,Validity_Period)
        time.sleep(Interval)

def stop_control_button():
    global thredcounter
    thredcounter=thredcounter+1

app = gui()
app.setSize(600,520)
app.addLabel("title", "Robot Operator")

#Configure the GUI

# Brief explanation

app.startFrame("LEFT", row=0, column=0)

app.addMessage("welcome", """- Choose controller by inputting IP:PORT
- Select option
- Value: [0,100] for Packet Loss, [0,1] for Transmission Loss, [0,0.3] for Delay 
- Save and press start!""")
app.setMessageWidth("welcome", 700)
 
# Features
app.addLabelEntry("Controller IP:")
app.setEntry("Controller IP:", "192.168.40.11:32149")
row = app.getRow()
app.addRadioButton("Option", "Normal operation")
app.addRadioButton("Option", "Packet Loss")
app.addRadioButton("Option", "Transmission Loss")
app.addRadioButton("Option", "Delay")
app.addLabelNumericEntry("Value:")
app.addButtons(["Save settings","Reset"], save_opt)# You save settings here
app.addHorizontalSeparator()

# Start/stop and status bar
app.addLabel("title2", "INITIATE COMMUNICATION WITH THE CONTROLLER")
app.addButtons(["Start", "Stop"], start_stop)
app.addLabel("Status", "Stopped")
app.setLabelBg("Status", "red")
app.addHorizontalSeparator()

# Pendulum control
app.addLabel("title3", "PENDULUM CONTROL")
app.addButtons(["Confirm steady state","Safe exit"], pendulum_control)
app.addHorizontalSeparator()
app.stopFrame()



# Motion control
app.startFrame("Motion", row=1, column=0,colspan=2)
app.addLabel("title4", "MOTION CONTROL",colspan=2)

app.addLabelEntry("Validity Period [ms]:",1,0)
app.setEntry("Validity Period [ms]:", "1000")

app.addLabelEntry(" Interval: ",1,1)
app.setEntry(" Interval: ", "1000")
row = app.getRow()
app.addLabelScale("Power",row,0)
app.setScaleRange("Power", -100, 100)
app.showScaleValue("Power", show = True)
app.setScale("Power",0, callFunction =True )
app.setScaleChangeFunction("Power", motion_thread_manage)
app.addButtons(["Stop Motion Control "], stop_control_button,row,1)
app.addHorizontalSeparator(colspan=2)
app.stopFrame()

#Attacker
'''
app.addLabel("title5", "ATTACKER",colspan=2)
row = app.getRow()
app.addLabelEntry("Attack Validity Period [ms]:",row,0)
app.setEntry("Attack Validity Period [ms]:", "500")
app.addLabelEntry(" Attack Interval: ",row,1)
app.setEntry(" Attack Interval: ", "500")
row = app.getRow()
app.addButtons(["Attack"], attack_thread_manage,row,0)
app.addLabel("Attack States", "No attack/ Attack ends",row,1)
'''
app.go()

# Controller with integral action
import socket
import json
import time
import os  # Import the os module for accessing environment variables

# Get the host's IP address from the environment variable
HOST_IP = os.getenv('HOST_IP')

# Use the host's IP address for listening
# UDP_IP = HOST_IP if HOST_IP else '0.0.0.0'
# K - controler gain (observer based feedback implemented)  
K =  [-0.60, -.02,  .01]   # Adjust PID controller parameters based on the environment of the robot is experiencing
# Initialise some parameters:
theta_hat = [0, 0, 0]   # Initialise observer states
integral_action = 0     # Initialise integral action  
F = 0                   # Initialise output
F_old = 0               # Initialise old output (used when dropout occurs)
maxVolt = 9             # Largest allowed voltage
restart = 0

UDP_IP = '0.0.0.0'  # This is the IP of the raspberry PI and the server listening ports on it
# UDP_PORT_GUI = 32150 
UDP_PORT_MEAS = 5007
print(HOST_IP)
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((UDP_IP, UDP_PORT_MEAS))
integral_error = 0
error = 0
error_old = 0
start_time = time.time()
desired_angle = 90
hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname)   
print("Your Computer Name is:"+hostname)   
print("Your Computer IP Address is:"+IPAddr)  
print("Controller is ready...")
active = 0
while True:
    time_meas = time.time()
    try:
        data, address = server.recvfrom(1024)
        measurement = json.loads(data.decode('utf-8'))
    except KeyboardInterrupt:
        break
    t_new = time.time()
    time_difference = t_new - time_meas
    
    motor_angle = measurement["motor_angle"]
    active = measurement["active"]
    error = motor_angle - desired_angle
    if abs(error) > (50):
        keep = 0
        F = 0
        integral_error += 0
        print("Pendulum fell, it is a disaster...")
        try:
            # Send control signal over UDP to Raspberry Pi
            message = {'control_signal': 0}
            message = json.dumps(message).encode('utf-8')
            server.sendto(message,address)
            #print(message)
        except KeyboardInterrupt:
            print("Exiting program")
            server.close()
        
    else:
        if active:
            integral_error += (error * (time_difference))
        else:
            integral_error = 0
        # Get a control signal from the controller and update observer states
        F = -K[0] * error - K[1] * integral_error #- K[2] * ((error - error_old)/(time_difference)) 
    # print(error,integral_error,F,time_difference)
    if F > 100:
        F = 100
    if F < -100:
        F = -100
    error_old = error

    print(measurement,F,integral_error,time_difference)
    # Get user input for the control signal
    try:
        # Send control signal over UDP to Raspberry Pi
        
        message = {'control_signal': F}
        message = json.dumps(message).encode('utf-8')
        server.sendto(message, address)
    except KeyboardInterrupt:
        print("Exiting program")
        server.close()


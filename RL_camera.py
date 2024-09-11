import socket,json,time
import numpy as np
import gym
from stable_baselines3 import PPO,TD3
from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise

# Constants
UDP_IP_ROBOT = "192.168.10.11"  # Replace with the actual IP address of your robot
OBSERVATION_SPACE_DIM = 2  
ACTION_SPACE_DIM = 1  

UDP_IP = '0.0.0.0'  # Use '0.0.0.0' to bind to all available interfaces
UDP_PORT = 5005

sock_command = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_command.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_command.bind((UDP_IP, 5006))
sock_reset = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Listening for UDP messages on {UDP_IP}:{UDP_PORT}")

# Create a custom Gym environment
class RobotEnvironment(gym.Env):
    def __init__(self):
        super(RobotEnvironment, self).__init__()
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(OBSERVATION_SPACE_DIM,))
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(ACTION_SPACE_DIM,))
        self.current_angle = 0.0
        self.cum_rew = 0
        self.step_count = 0
        self.step_total = 0
        self.err = 0
        self.action = 0
        self.time_meas = 0
        self.timer = time.time()
    def get_request(self):
        #a = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 5005))
        try:
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            received_message = data.decode('utf-8')
                # Decode received data
            received_message = json.loads(data.decode('utf-8'))
                # Extract motor angle and generation time
            motor_angle = received_message.get("motor_angle", None)
            id = received_message.get("id", None)
            #print(f"motor angle:{motor_angle}, id: {id}")     
            #time.sleep(0.00000001)  
            return motor_angle
        except KeyboardInterrupt:
            print("Exiting program")
        finally:
            sock.close()
        return motor_angle
    def reset(self):
        # Reset the environment
        self.cum_rew = 0
        self.step_total = 0
        self.timer = time.time()
        print("RESET")
        err = self.start_over()
        return np.array([self.get_request(),err])
    def command_action(self,action):
         # Get user input for the control signal
        try:
            control_signal = float(action)
            # Send control signal over UDP to Raspberry Pi
            message = {'control_signal': control_signal}
            sock_command.sendto(json.dumps(message).encode('utf-8'), (UDP_IP_ROBOT, 5006))
        except KeyboardInterrupt:
            print("Exiting program")
            sock_command.close()
        # time.sleep(0.01)
            
    def start_over(self,angle=90):
        # Get user input for the control signal
        try:
            # Send control signal over UDP to Raspberry Pi
            message = {'reset_motor': 1}
            message = json.dumps(message).encode('utf-8')
            sock_reset.sendto(message, ('192.168.10.11', 5008))
            print(message)
        except KeyboardInterrupt:
            print("Exiting program")
            sock_reset.close()
        a = self.get_request()
        t = time.time()
        time.sleep(1)
        
        self.time_meas = time.time()
        print("Ready to start...")
        return (self.get_request() - a ) / (time.time() - t)
    def step(self, action):
        # Take a step in the environment 
        
        self.command_action(action[0]*40)
        self.curr = self.get_request()
        print(self.curr )
        #print(f"Sec Meas:{time.time()}")
        self.err = (self.curr - self.current_angle ) / (time.time() - self.time_meas)
        self.time_meas = time.time()
        # Calculate the reward (e.g., based on the difference between the desired and current angle)

        self.current_angle = self.curr
        # reward = -((self.current_angle - (-90))/ 180 * np.pi ) ** 2 - 0.003 * (self.err / 180 * np.pi ) ** 2
        if abs(self.current_angle - (90)) < 5:
            reward = 100
        elif  abs(self.current_angle - (90)) >= 5 and abs(self.current_angle - (90)) <= 30: 
            reward = -1 * abs(self.current_angle - (90)) 
        else:
            reward = -1000
        self.cum_rew += reward 
        # Check if the episode is done (you may need to define your own termination conditions)
        info = {}
        
        self.step_total += 1
        if abs(self.current_angle - (90)) > 40:
            done = True
            info = {"Total Reward": self.cum_rew,"Step Count": self.step_total,"Episode":self.step_count}
            print("---------------------------------------")
            print(info)
            print("---------------------------------------")
            self.step_count += 1
            
        else:
            done = False
            info1 = {"Reward": reward,"Step Count": self.step_total,"Angle": self.current_angle,"Angle Dot": self.err}
            print(info1)
        self.action = action[0]
        return np.array([self.current_angle,self.err]), reward, done, info 
typr = 1
if typr:
    # Instantiate the environment
    env = RobotEnvironment()
    model = PPO("MlpPolicy", env, verbose=0)
    print("Learning starts...")
    model.learn(total_timesteps=256*3000)
    # Save the trained model
    model.save("ppo_robot_model3")
else:
    # Load the trained model
    model = PPO.load("ppo_robot_model3")
    # Instantiate the environment
    env = RobotEnvironment()
    obs = env.reset()
    while True:
        action, _states = model.predict(obs)
        obs, reward, done, info = env.step(action)




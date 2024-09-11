## Objective
The goal of this project is to demonstrate a real-time edge computing application with strict latency requirements. 

## System Components
- **Rover with Inverted Pendulum**: A compact, battery-powered rover equipped with an inverted pendulum. We used Dexter Industries BrickPi3 robot (https://github.com/DexterInd/BrickPi3) where we mounted an inverted pendulum with lego parts 
- **Camera for Angle Estimation**: A camera that captures the pendulum’s angle in real time for feedback control.
- **Communication Latency Monitor**: Monitors the latency in data transmission to ensure the system responds within required time frames.
- **Offloading Orchestrator**: Dynamically selects the appropriate controller (either in the edge or user computer) based on current network latency experienced, ensuring optimal performance.


### System Flow: Time Diagram

1. **User Input**  
   The user controls the robot with the inverted pendulum by interacting with their equipment (e.g., a laptop), sending commands to move the robot forward or backward. These commands introduce disturbances to the pendulum.

2. **Camera Vision**  
   A camera attached to the system captures real-time video frames and detects two heart shapes that are used to calculate the pendulum's angle.

3. **UDP Transmission**  
   The measured pendulum angle is transmitted using the UDP protocol to the controller algorithms running both on the edge server and the user's local computer.

4. **Servo Controller**  
   The controller algorithms, which receive the angle data, work to stabilize the pendulum by adjusting the servo motor in response to the angle. This implementation allows to use two controller algorithms. You can either use PID controller in controllerF.py or RL controller in RL_camera.py. 

5. **Latency Measurement**  
   A latency monitor measures the communication delays between the system components. It determines the current network conditions.

6. **Orchestrator Decision**  
   Based on the measured latency, the orchestrator dynamically decides whether to use the edge server or the user's local computer to process the controller algorithms, with the goal of minimizing the overall communication latency.

Following gif shows how the implementation works in a real private network. 


![Rover Balancing in Action](/UI.gif)


More details could be found in the poster presentation added to the repo (inverted demo poster.pdf).

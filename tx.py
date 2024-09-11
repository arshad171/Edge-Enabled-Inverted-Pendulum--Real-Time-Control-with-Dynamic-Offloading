import socket
import json
import sys
# a new version with validity period
def tx(function,seq,value,Validity_Period,direction=0):
    UDP_IP = '0.0.0.0'
    UDP_PORT=5080
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #server.bind((UDP_IP, UDP_PORT))
    server.settimeout(0.3)
    address=('192.168.10.11', 32152) # the address of the RPi
    if 'd' in function: #send the data
        result = {"PacketType": 'ControlMessage', "Seq": seq, 'PowerValue': value, "Risk": 'unknown',
                  "ValidityPeriod": Validity_Period,"direction":direction}
        print(result)
    controlOutput = json.dumps(result).encode('utf-8')
    server.sendto(controlOutput, address)

    address = ('130.237.43.63', 6001)
    server.sendto(controlOutput, address)

if __name__ == "__main__":
    function = sys.argv[1]
    seq = int(sys.argv[2])
    value= sys.argv[3]
    tx(function,seq,value)

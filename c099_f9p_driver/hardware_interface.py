import serial
import pynmea2

# serial configuration
port = '/dev/ttyUSB0'
baudrate = 460800
bytesize = serial.EIGHTBITS
parity = serial.PARITY_NONE
stopbits = serial.STOPBITS_ONE
timeout = 0.1

position_data = 'GGA'
velvector_data = 'RMC'


def position():
    with serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout) as ser:
        while True:
            line = ser.readline().decode('ascii', errors='replace')
            if position_data in line:
                msg = pynmea2.parse(line)
                print(msg)
                print("---------")
                print(msg.latitude, msg.longitude)
                print("---------")
                print(msg.longitude)
                print("---------")
                #return line.strip()

def velocity():
    pass

def angle():
    pass

position()
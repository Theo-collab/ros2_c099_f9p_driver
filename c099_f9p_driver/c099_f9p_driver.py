import io

import rclpy
import time
from rclpy.node import Node
from std_msgs.msg import String

import pynmea2
import serial

# serial configuration
port = '/dev/ttyUSB0'
baudrate = 460800
bytesize = serial.EIGHTBITS
parity = serial.PARITY_NONE
stopbits = serial.STOPBITS_ONE
timeout = 0.1

position_data = 'GGA'
velvector_data = 'RMC'


ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

class GnssPublisher(Node):

    def __init__(self):
        super().__init__('gnss_publisher')
        self.publisher_ = self.create_publisher(String, 'gnss/position', 10)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.gnss_callback)

    def gnss_callback(self):
        msg = String()
        try:
            line = sio.readline()
            f = open('/home/ubuntu/positions.txt', 'a')
            if position_data in line:
                location_raw = pynmea2.parse(line)
                location = location_raw.longitude, location_raw.latitude, location_raw.altitude
                f.write(str(location_raw.longitude))
                f.write(",")
                f.write(str(location_raw.latitude))
                f.write(",")
                f.write(str(location_raw.altitude))
                f.write("\n")
                msg.data = f"Position: {location}"
                self.publisher_.publish(msg)
                self.get_logger().info('Publishing: "%s"' % msg.data)
                #print(repr(msg))
            f.close()
        except serial.SerialException as e:
            print('Device error: {}'.format(e))
        except pynmea2.ParseError as e:
            print('Parse error: {}'.format(e))


def main(args=None):
    rclpy.init(args=args)

    gnss_publisher = GnssPublisher()
    
    rclpy.spin(gnss_publisher)

    gnss_publisher.destroy_node()
    rclpy.shutdown()

import io

import rclpy
import time
import datetime

from rclpy.node import Node
from std_msgs.msg import String

import pynmea2
import serial

# serial configuration
port = '/dev/ttyACM0'
baudrate = 460800
bytesize = serial.EIGHTBITS
parity = serial.PARITY_NONE
stopbits = serial.STOPBITS_ONE
timeout = 0.1

# board gives: GGA, GSA, GSV, GLL, RMC, VTG

#msg = pynmea2.parse("$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D")
# TODO: fur i in msg.fields add it to publishable message
#msg.fields
#type(msg).__name__
#TODO instantiate ros2 message type depending on this

ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

file = '/home/jetson/positionlog_'+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

class GnssPublisher(Node):

    def __init__(self):
        super().__init__('gnss_publisher')
        self.publisher_ = self.create_publisher(String, 'gnss/position', 10)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.gnss_callback)

    def gnss_callback(self):
        msg = String()
        try:
            line = pynmea2.parse(sio.readline())
            f = open(file, 'a')
            if type(line).__name__ == 'VTG':
                speed = line.spd_over_grnd_kmph
                msg.data = f"{type(line).__name__}: Speed over Ground: {speed}"
                self.publisher_.publish(msg)
                self.get_logger().info('Publishing: "%s"' % msg.data)

            if type(line).__name__ == 'GLL' or type(line).__name__ == 'RMC':
                location = line.longitude, line.latitude
                msg.data = f"{type(line).__name__}: Position: {location}"
                self.publisher_.publish(msg)
                self.get_logger().info('Publishing: "%s"' % msg.data)

            if type(line).__name__ == 'GGA':
                location = line.longitude, line.latitude, line.altitude
                msg.data = f"{type(line).__name__}: Position: {location}"
                self.publisher_.publish(msg)
                self.get_logger().info('Publishing: "%s"' % msg.data)
                f.write(str(line.longitude))
                f.write(",")
                f.write(str(line.latitude))
                f.write(",")
                f.write(str(line.altitude))
                f.write("\n")
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

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Float64
import serial
import smbus2
from pyubx2 import UBXReader
from hmc5883l import hmc5883l

class GpsCompassNode(Node):
    def __init__(self):
        super().__init__('gps_compass_node')

        # Parameters
        self.declare_parameter('gps_port', '/dev/ttyTHS1')
        self.declare_parameter('baudrate', 38400)
        self.declare_parameter('compass_address', 0x1E)

        port = self.get_parameter('gps_port').value
        baud = self.get_parameter('baudrate').value
        self.compass_address = self.get_parameter('compass_address').value

        # Publishers
        self.gps_pub = self.create_publisher(NavSatFix, 'gps/fix', 10)
        self.compass_pub = self.create_publisher(Float64, 'compass/headingDeg', 10)

        # Serial connection
        self.ser = serial.Serial(port, baud, timeout=0.5)
        self.parser = UBXReader(self.ser, protfilter=2)

        # I2C bus for compass
        try:
            self.bus = smbus2.SMBus(1)
        except Exception as e:
            self.get_logger().warn(f'Compass I2C init failed: {e}')
            self.bus = None

        self.compass = hmc5883l()

        self.create_timer(0.1, self.read_gps)
        self.create_timer(0.2, self.read_compass)

    def read_gps(self):
        try:
            (raw_data, parsed) = self.parser.read()
            if parsed.identity == 'NAV-POSLLH':
                msg = NavSatFix()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.latitude = parsed.lat
                msg.longitude = parsed.lon
                msg.altitude = parsed.hMSL * 1e-3
                self.gps_pub.publish(msg)
        except Exception as e:
            self.get_logger().warn(f'GPS parse error: {e}')


    def read_compass(self):
        if not self.bus:
            return
        try:
            heading = Float64()
            heading.data = self.compass.heading()
            self.compass_pub.publish(heading)
        except Exception as e:
            self.get_logger().warn(f'Compass read failed: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = GpsCompassNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

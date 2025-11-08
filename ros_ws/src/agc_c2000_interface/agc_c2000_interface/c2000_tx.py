import rclpy
from rclpy.node import Node
from agc_msgs.msg import C2000Command
import serial
import struct
import threading

class C2000Tx(Node):
    def __init__(self):
        super().__init__('c2000_tx')

        # --- params
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baud', 115207)
        self.declare_parameter('write_on_change', True)  # else, send at fixed rate
        self.declare_parameter('rate_hz', 50)            # if write_on_change=False

        port = self.get_parameter('port').get_parameter_value().string_value
        baud = self.get_parameter('baud').get_parameter_value().integer_value

        # Open serial
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.05,
                write_timeout=0.05,
            )
        except Exception as e:
            self.get_logger().fatal(f'Failed to open {port}: {e}')
            raise

        self.get_logger().info(f'Opened {port} @ {baud}')

        self.lock = threading.Lock()
        self.latest = C2000Command()  # zeros by default

        self.sub = self.create_subscription(
            C2000Command, 'c2000/cmd', self.cb_cmd, 10
        )

        self.write_on_change = self.get_parameter('write_on_change').value
        if not self.write_on_change:
            rate = float(self.get_parameter('rate_hz').value)
            self.timer = self.create_timer(1.0 / rate, self.tx_latest)

    # ----- pack as [uint8, uint8, uint8, float32] little-endian
    # Simulink Byte Unpack:
    #   dims: {{[1],[1],[1],[1]}}
    #   types: {'uint8','boolean','boolean','single'}
    #   alignment: 1
    def pack_frame(self, msg: C2000Command) -> bytes:
        thr_cmd = int(msg.motor_thr_cmd) & 0xFF
        thr_dir = 1 if msg.motor_thr_dir else 0
        thr_brk = 1 if msg.motor_thr_brk else 0
        angle   = float(msg.shaft_angle_cmd)

        # '<' little-endian, B B B f  (NO padding)
        return struct.pack('<BBBf', thr_cmd, thr_dir, thr_brk, angle)

    def write_bytes(self, payload: bytes):
        try:
            with self.lock:
                self.ser.write(payload)
        except Exception as e:
            self.get_logger().error(f'Write failed: {e}')

    def cb_cmd(self, msg: C2000Command):
        self.latest = msg
        if self.write_on_change:
            self.write_bytes(self.pack_frame(msg))

    def tx_latest(self):
        self.write_bytes(self.pack_frame(self.latest))

def main():
    rclpy.init()
    node = C2000Tx()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

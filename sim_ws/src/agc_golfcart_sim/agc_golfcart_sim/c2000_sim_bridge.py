#!/usr/bin/env python3
"""
C2000 Simulation Bridge Node

Bridges between Gazebo simulation and TI C2000 microcontroller for HIL testing.
Reads simulated sensor data from Gazebo and sends to C2000 via serial.
Receives motor commands from C2000 and forwards to Gazebo effort controllers.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
import serial
import struct
import threading
import math

"""Bridge node between Gazebo simulation and C2000 microcontroller"""
class C2000SimBridge(Node):
    # Packet protocol constants
    START_BYTE = 0xAA
    END_BYTE = 0x55
    SENSOR_PACKET_ID = 0x01
    MOTOR_PACKET_ID = 0x02
    
    def __init__(self):
        super().__init__('c2000_sim_bridge')
        
        # Declare and get parameters
        self._declare_parameters()
        self._load_parameters()
        
        # Initialize state variables
        self.steering_angle = 0.0  # radians
        self.drive_velocity = 0.0  # rad/s
        self.steering_encoder_counts = 0
        self.drive_encoder_counts = 0
        
        # Motor command state (received from C2000)
        # Steering: Sabertooth format 0-127 uint8 (0-63 reverse, 64=stop, 65-127 forward)
        # Drive: Percentage format -100 to +100 int8
        self.steering_motor_cmd = 64  # Sabertooth format: 0-127 (64 = stop)
        self.drive_motor_cmd = 0      # Percentage format: -100 to +100 (0 = stop)
        
        # Initialize serial port
        self.serial_port = None
        self.serial_connected = False
        self._init_serial()
        
        # Setup subscribers
        self.joint_states_sub = self.create_subscription(
            JointState,
            self.joint_states_topic,
            self.joint_states_callback,
            10
        )
        
        # Setup publishers for effort commands
        self.steering_cmd_pub = self.create_publisher(
            Float64MultiArray,
            self.steering_command_topic,
            10
        )
        
        self.drive_cmd_pub = self.create_publisher(
            Float64MultiArray,
            self.drive_command_topic,
            10
        )
        
        # Create timer for periodic sensor feedback transmission
        self.timer = self.create_timer(
            1.0 / self.update_rate,
            self.timer_callback
        )
        
        # Start serial receive thread
        if self.serial_connected:
            self.running = True
            self.receive_thread = threading.Thread(target=self._serial_receive_loop, daemon=True)
            self.receive_thread.start()
        
        self.get_logger().info('C2000 Simulation Bridge initialized')
        self.get_logger().info(f'Serial port: {self.serial_port_name} @ {self.baud_rate} baud - Connected: {self.serial_connected}')
        self.get_logger().info(f'Update rate: {self.update_rate} Hz')
        self.get_logger().info(f'Subscribing to: {self.joint_states_topic}')
        self.get_logger().info(f'Publishing steering commands to: {self.steering_command_topic}')
        self.get_logger().info(f'Publishing drive commands to: {self.drive_command_topic}')
    
    """Initialize serial connection to C2000"""
    def _init_serial(self):
        try:
            self.serial_port = serial.Serial(
                port=self.serial_port_name,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1
            )
            self.serial_connected = True
            self.get_logger().info(f'Serial port {self.serial_port_name} opened successfully')
        except serial.SerialException as e:
            self.get_logger().warn(f'Failed to open serial port: {e}. Running without C2000 connection.')
            self.serial_connected = False
    
    """Declare all ROS parameters with default values"""
    def _declare_parameters(self):
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('baud_rate', 250000)
        self.declare_parameter('update_rate', 50.0)
        self.declare_parameter('joint_states_topic', '/joint_states')
        self.declare_parameter('steering_command_topic', '/steering_controller/commands')
        self.declare_parameter('drive_command_topic', '/rear_drive_controller/commands')
        self.declare_parameter('steering_encoder_cpr', 2400)
        self.declare_parameter('drive_encoder_cpr', 2400)
        self.declare_parameter('steering_joint_name', 'steering_input_joint')
        self.declare_parameter('drive_joint_name', 'rear_left_wheel_joint')
        self.declare_parameter('steering_max_torque', 4.90)
        self.declare_parameter('drive_max_torque', 50.0)

    """Load parameters from parameter server"""
    def _load_parameters(self):
        self.serial_port_name = self.get_parameter('serial_port').value
        self.baud_rate = self.get_parameter('baud_rate').value
        self.update_rate = self.get_parameter('update_rate').value
        self.joint_states_topic = self.get_parameter('joint_states_topic').value
        self.steering_command_topic = self.get_parameter('steering_command_topic').value
        self.drive_command_topic = self.get_parameter('drive_command_topic').value
        self.steering_encoder_cpr = self.get_parameter('steering_encoder_cpr').value
        self.drive_encoder_cpr = self.get_parameter('drive_encoder_cpr').value
        self.steering_joint_name = self.get_parameter('steering_joint_name').value
        self.drive_joint_name = self.get_parameter('drive_joint_name').value
        self.steering_max_torque = self.get_parameter('steering_max_torque').value
        self.drive_max_torque = self.get_parameter('drive_max_torque').value   

    """Process incoming joint states from Gazebo"""    
    def joint_states_callback(self, msg):
        try:
            # Find steering joint
            if self.steering_joint_name in msg.name:
                idx = msg.name.index(self.steering_joint_name)
                self.steering_angle = msg.position[idx]
                # Convert angle to encoder counts
                self.steering_encoder_counts = int(
                    (self.steering_angle / (2.0 * math.pi)) * self.steering_encoder_cpr
                )
            
            # Find drive joint
            if self.drive_joint_name in msg.name:
                idx = msg.name.index(self.drive_joint_name)
                self.drive_velocity = msg.velocity[idx]
                # Convert position (radians) to encoder counts
                # Full rotation (2π radians) = drive_encoder_cpr counts
                joint_position = msg.position[idx]
                self.drive_encoder_counts = int(
                    (joint_position / (2.0 * math.pi)) * self.drive_encoder_cpr
                )
        
        except (ValueError, IndexError) as e:
            self.get_logger().warn(f'Error processing joint states: {e}', throttle_duration_sec=5.0)

    """Send sensor data packet to C2000"""
    def _send_sensor_data(self):
        if not self.serial_connected:
            return
        
        try:
            # Packet structure: [START][ID][STEER_ENC(4)][DRIVE_ENC(4)][CHECKSUM][END]
            # Total: 12 bytes
            packet = struct.pack(
                '<BBiiB',  # little-endian: byte, byte, int32, int32, byte
                self.START_BYTE,
                self.SENSOR_PACKET_ID,
                self.steering_encoder_counts,
                self.drive_encoder_counts,
                self.END_BYTE
            )
            
            self.serial_port.write(packet)
            self.get_logger().debug(
                f'TX -> Steer: {self.steering_encoder_counts}, Drive: {self.drive_encoder_counts}',
                throttle_duration_sec=1.0
            )
            
        except serial.SerialException as e:
            self.get_logger().error(f'Serial write error: {e}')
            self.serial_connected = False

    """Background thread to receive motor commands from C2000"""
    def _serial_receive_loop(self):
        while self.running and self.serial_connected:
            try:
                # Wait for start byte
                if self.serial_port.in_waiting > 0:
                    byte = self.serial_port.read(1)
                    if byte[0] == self.START_BYTE:
                        # Read packet ID
                        packet_id = self.serial_port.read(1)[0]
                        
                        if packet_id == self.MOTOR_PACKET_ID:
                            # Motor command packet: [START][ID][STEER_CMD(1)][DRIVE_CMD(1)][END]
                            # Steering: Sabertooth 0-127 uint8
                            # Drive: Percentage -100 to +100 int8
                            # Total: 5 bytes (3 remaining after start and ID)
                            data = self.serial_port.read(3)

                            if len(data) == 3 and data[2] == self.END_BYTE:
                                # Unpack motor commands
                                # B = unsigned char (0-255), b = signed char (-128 to 127)
                                steer_cmd, drive_cmd = struct.unpack('<Bb', data[0:2])

                                self.steering_motor_cmd = steer_cmd
                                self.drive_motor_cmd = drive_cmd

                                self.get_logger().debug(
                                    f'RX <- Steer cmd: {steer_cmd} (0-127), Drive cmd: {drive_cmd} (-100 to +100)',
                                    throttle_duration_sec=1.0
                                )

                                # Publish to effort controllers
                                self._publish_motor_commands()
                            
            except Exception as e:
                self.get_logger().error(f'Serial receive error: {e}')

    """Convert motor commands to effort and publish"""
    def _publish_motor_commands(self):
        # Steering: Convert Sabertooth format (0-127 uint8) to effort
        # 0-63: reverse (-100% to 0%), 64: stop (0%), 65-127: forward (0% to +100%)
        if self.steering_motor_cmd < 64:
            # Reverse: 0 maps to -100%, 63 maps to ~0%
            steering_normalized = (self.steering_motor_cmd - 64) / 64.0
        elif self.steering_motor_cmd == 64:
            # Stop
            steering_normalized = 0.0
        else:
            # Forward: 65 maps to ~0%, 127 maps to +100%
            steering_normalized = (self.steering_motor_cmd - 64) / 63.0

        steering_effort = steering_normalized * self.steering_max_torque

        # Drive: Convert percentage format (-100 to +100) to effort
        # -100 = full reverse, 0 = stop, +100 = full forward
        drive_normalized = self.drive_motor_cmd / 100.0
        drive_effort = drive_normalized * self.drive_max_torque

        # Publish steering command
        steering_msg = Float64MultiArray()
        steering_msg.data = [steering_effort]
        self.steering_cmd_pub.publish(steering_msg)

        # Publish drive command (both rear wheels)
        drive_msg = Float64MultiArray()
        drive_msg.data = [drive_effort, drive_effort]
        self.drive_cmd_pub.publish(drive_msg)

    """Periodic callback to send sensor data to C2000 and handle incoming commands"""
    def timer_callback(self):
        # Send encoder counts to C2000
        self._send_sensor_data()
        
        # Log current state periodically
        if self.serial_connected:
            self.get_logger().debug(
                f'State - Steer enc: {self.steering_encoder_counts}, '
                f'Drive enc: {self.drive_encoder_counts}, '
                f'Steer cmd: {self.steering_motor_cmd} (0-127), Drive cmd: {self.drive_motor_cmd} (-100 to +100)',
                throttle_duration_sec=2.0
            )
        
    """Helper function to send test commands to effort controllers"""    
    def send_test_command(self, steering_effort=0.0, drive_effort=0.0):
        # Steering command
        steering_msg = Float64MultiArray()
        steering_msg.data = [steering_effort]
        self.steering_cmd_pub.publish(steering_msg)
        
        # Drive command
        drive_msg = Float64MultiArray()
        drive_msg.data = [drive_effort, drive_effort]  # Both rear wheels
        self.drive_cmd_pub.publish(drive_msg)
        
        self.get_logger().info(f'Sent test commands - Steering: {steering_effort}, Drive: {drive_effort}')
    
    def destroy_node(self):
        """Cleanup on shutdown"""
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = C2000SimBridge()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
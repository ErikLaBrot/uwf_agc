#!/usr/bin/env python3
"""C2000 Simulation Bridge Node

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


class C2000SimBridge(Node):
    """Bridge node between Gazebo simulation and C2000 microcontroller."""

    # Packet protocol constants
    START_BYTE = 0xAA
    END_BYTE = 0x55
    SENSOR_PACKET_ID = 0x01
    MOTOR_PACKET_ID = 0x02

    def __init__(self) -> None:
        super().__init__('c2000_sim_bridge')

        # Declare and load parameters
        self._declare_parameters()
        self._load_parameters()

        # Initialize state variables
        self.steering_angle = 0.0          # radians
        self.drive_velocity = 0.0          # rad/s

        # QEP-style encoder counts
        # Steering starts in the middle of 32-bit range (like a centered QEP)
        self.steering_encoder_counts = self.steering_encoder_center
        # Drive starts at 0 and accumulates
        self.drive_encoder_counts = 0

        # Last joint angles for incremental encoder emulation
        self._last_steering_angle = None
        self._last_drive_angle = None

        # Motor command state (received from C2000)
        # Steering: Sabertooth format 0-127 uint8 (0-63 reverse, 64=stop, 65-127 forward)
        self.steering_motor_cmd = 64       # Sabertooth format: 0-127 (64 = stop)

        # Throttle and brake: normalized 0-1 commands from C2000 PI controllers
        self.throttle_cmd_u = 0.0
        self.brake_cmd_u = 0.0

        # Initialize serial port
        self.serial_port = None
        self.serial_connected = False
        self._init_serial()

        # Setup subscribers
        self.joint_states_sub = self.create_subscription(
            JointState,
            self.joint_states_topic,
            self.joint_states_callback,
            10,
        )

        # Setup publishers for effort commands
        self.steering_cmd_pub = self.create_publisher(
            Float64MultiArray,
            self.steering_command_topic,
            10,
        )
        self.drive_cmd_pub = self.create_publisher(
            Float64MultiArray,
            self.drive_command_topic,
            10,
        )

        # Create timer for periodic sensor feedback transmission
        self.timer = self.create_timer(
            1.0 / self.update_rate,
            self.timer_callback,
        )

        # Serial receive thread control
        self.running = True
        if self.serial_connected:
            self.receive_thread = threading.Thread(
                target=self._serial_receive_loop,
                daemon=True,
            )
            self.receive_thread.start()
        else:
            self.receive_thread = None
            self.get_logger().warn(
                'Starting without C2000 serial connection, '
                'bridge will run without serial I/O.'
            )

        self.get_logger().info('C2000SimBridge node initialized')

    def _init_serial(self) -> None:
        """Initialize the serial port connection to the C2000."""
        try:
            self.serial_port = serial.Serial(
                port=self.serial_port_name,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1,
            )
            self.serial_connected = True
            self.get_logger().info(
                f'Serial port {self.serial_port_name} opened successfully'
            )
        except serial.SerialException as e:
            self.get_logger().warn(
                f'Failed to open serial port: {e}. Running without C2000 connection.'
            )
            self.serial_connected = False

    def _declare_parameters(self) -> None:
        """Declare all ROS parameters with default values."""
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        # You found 500000 works reliably with the CP210x
        self.declare_parameter('baud_rate', 500000)
        self.declare_parameter('update_rate', 100.0)

        self.declare_parameter('joint_states_topic', '/joint_states')
        self.declare_parameter('steering_command_topic', '/steering_controller/commands')
        self.declare_parameter('drive_command_topic', '/rear_drive_controller/commands')

        # Encoder config
        self.declare_parameter('steering_encoder_cpr', 2400)
        self.declare_parameter('drive_encoder_cpr', 2400)
        # Center value for steering QEP (mid of 32-bit range)
        self.declare_parameter('steering_encoder_center', 0x80000000)
        # Steering column / joint ratio: column_rad = ratio * joint_rad
        self.declare_parameter('steering_gear_ratio', 1.0)

        self.declare_parameter('steering_joint_name', 'steering_input_joint')
        self.declare_parameter('drive_joint_name', 'rear_left_wheel_joint')

        self.declare_parameter('steering_max_torque', 4.90)
        self.declare_parameter('drive_max_torque', 50.0)
        self.declare_parameter('brake_max_torque', 50.0)
        self.declare_parameter('brake_velocity_threshold', 0.05)

    def _load_parameters(self) -> None:
        """Load parameters from the parameter server into instance attributes."""
        p = self.get_parameter

        self.serial_port_name = p('serial_port').value
        self.baud_rate = p('baud_rate').value
        self.update_rate = p('update_rate').value

        self.joint_states_topic = p('joint_states_topic').value
        self.steering_command_topic = p('steering_command_topic').value
        self.drive_command_topic = p('drive_command_topic').value

        self.steering_encoder_cpr = int(p('steering_encoder_cpr').value)
        self.drive_encoder_cpr = int(p('drive_encoder_cpr').value)
        self.steering_encoder_center = int(
            p('steering_encoder_center').value
        ) & 0xFFFFFFFF
        # Steering column / joint ratio
        self.steering_gear_ratio = float(p('steering_gear_ratio').value)

        self.steering_joint_name = p('steering_joint_name').value
        self.drive_joint_name = p('drive_joint_name').value

        self.steering_max_torque = float(p('steering_max_torque').value)
        self.drive_max_torque = float(p('drive_max_torque').value)
        self.brake_max_torque = float(p('brake_max_torque').value)
        self.brake_velocity_threshold = float(p('brake_velocity_threshold').value)

        self.get_logger().info(
            f'Parameters - serial_port: {self.serial_port_name}, '
            f'baud_rate: {self.baud_rate}, update_rate: {self.update_rate} Hz, '
            f'steering_gear_ratio: {self.steering_gear_ratio}'
        )


    def joint_states_callback(self, msg: JointState) -> None:
        """Process incoming joint states from Gazebo.

        Updates internal joint angles, velocities, and QEP-style encoder counts.
        """
        try:
            name_to_index = {name: i for i, name in enumerate(msg.name)}

            # Steering joint
            if self.steering_joint_name in name_to_index:
                idx = name_to_index[self.steering_joint_name]
                angle = msg.position[idx]
                self.steering_angle = angle
                self._update_steering_encoder(angle)

            # Drive joint (use one rear wheel as reference)
            if self.drive_joint_name in name_to_index:
                idx = name_to_index[self.drive_joint_name]
                self.drive_velocity = msg.velocity[idx]  # rad/s
                drive_angle = msg.position[idx]
                self._update_drive_encoder(drive_angle)

        except (ValueError, IndexError) as e:
            self.get_logger().warn(f'Error processing joint states: {e}')

    def _update_steering_encoder(self, angle_rad: float) -> None:
        """Incremental steering QEP emulation, centered in mid of uint32 range."""
        if self._last_steering_angle is None:
            # First sample: treat current mechanical position as "center"
            self._last_steering_angle = angle_rad
            # counts already initialized to steering_encoder_center in __init__
            return

        delta_angle = angle_rad - self._last_steering_angle

        # Unwrap across ±π in case Gazebo wraps joint angles
        if delta_angle > math.pi:
            delta_angle -= 2.0 * math.pi
        elif delta_angle < -math.pi:
            delta_angle += 2.0 * math.pi

        # Apply steering gear ratio: column angle = ratio * joint angle
        column_delta = delta_angle * self.steering_gear_ratio

        # column angle → ticks (incremental)
        delta_ticks = int(
            round(
                column_delta
                * self.steering_encoder_cpr
                / (2.0 * math.pi)
            )
        )

        self.steering_encoder_counts = (
            self.steering_encoder_counts + delta_ticks
        ) & 0xFFFFFFFF  # emulate 32-bit wrap

        self._last_steering_angle = angle_rad


        self.steering_encoder_counts = (
            self.steering_encoder_counts + delta_ticks
        ) & 0xFFFFFFFF  # emulate 32-bit wrap

        self._last_steering_angle = angle_rad

    def _update_drive_encoder(self, angle_rad: float) -> None:
        """Incremental drive QEP emulation from wheel joint angle.

        Drive starts at 0 and accumulates ticks; C2000 side can just diff
        successive counts over time to estimate speed, like a real QEP.
        """
        if self._last_drive_angle is None:
            self._last_drive_angle = angle_rad
            return

        delta_angle = angle_rad - self._last_drive_angle

        # Unwrap across ±π in case of angle wrapping
        if delta_angle > math.pi:
            delta_angle -= 2.0 * math.pi
        elif delta_angle < -math.pi:
            delta_angle += 2.0 * math.pi

        delta_ticks = int(
            round(
                delta_angle
                * self.drive_encoder_cpr
                / (2.0 * math.pi)
            )
        )

        self.drive_encoder_counts = (
            self.drive_encoder_counts + delta_ticks
        ) & 0xFFFFFFFF

        self._last_drive_angle = angle_rad

    def _send_sensor_data(self) -> None:
        """Send simulated encoder counts to the C2000 over serial.

        Packet structure: [START][ID][STEER_ENC(int32)][DRIVE_ENC(int32)][END]
        Counts are maintained as uint32 in the bridge and converted to signed
        32-bit two's complement for transport, matching an int32 ByteUnpack
        on the C2000 side.
        """
        if not self.serial_connected:
            return

        try:
            # Internal counters are kept in uint32 range
            steer_u32 = int(self.steering_encoder_counts) & 0xFFFFFFFF
            drive_u32 = int(self.drive_encoder_counts) & 0xFFFFFFFF

            # Convert to signed 32-bit representation for struct.pack('i')
            if steer_u32 & 0x80000000:
                steer_i32 = steer_u32 - 0x100000000
            else:
                steer_i32 = steer_u32

            if drive_u32 & 0x80000000:
                drive_i32 = drive_u32 - 0x100000000
            else:
                drive_i32 = drive_u32

            packet = struct.pack(
                '<BBIIB',  # byte, byte, int32, int32, byte
                self.START_BYTE,
                self.SENSOR_PACKET_ID,
                steer_u32,
                drive_u32,
                self.END_BYTE,
            )

            self.serial_port.write(packet)
            self.get_logger().info(
                f'TX -> Steer enc: {steer_u32} (0x{steer_u32:08X}), '
                f'Drive enc: {drive_u32} (0x{drive_u32:08X})',
                throttle_duration_sec=1.0,
            )
        except serial.SerialException as e:
            self.get_logger().error(f'Error sending sensor data: {e}')
            self.serial_connected = False

    def _serial_receive_loop(self) -> None:
        """Background thread that receives motor commands from the C2000.

        Expects packets of the form:
        [START][MOTOR_PACKET_ID][STEER_CMD][THROTTLE_CMD][BRAKE_CMD][END]
        where:
          STEER_CMD    : uint8, 0-127 (Sabertooth format, 64 = stop)
          THROTTLE_CMD : uint8, 0-255 (normalized accel 0-1)
          BRAKE_CMD    : uint8, 0-255 (normalized brake 0-1)
        """
        while self.running and self.serial_connected:
            try:
                # Read start byte (blocking with timeout)
                start_byte = self.serial_port.read(1)
                if len(start_byte) == 0:
                    # Timeout with no data
                    continue

                if start_byte[0] != self.START_BYTE:
                    # Not a valid start byte, discard and continue
                    self.get_logger().info('Breaking at start byte!')
                    continue

                # Read packet ID
                packet_id_bytes = self.serial_port.read(1)
                if len(packet_id_bytes) == 0:
                    continue
                packet_id = packet_id_bytes[0]

                if packet_id == self.MOTOR_PACKET_ID:
                    # Expect [STEER_CMD][THROTTLE_CMD][BRAKE_CMD][END]
                    data = self.serial_port.read(4)
                    if len(data) != 4 or data[3] != self.END_BYTE:
                        # Malformed packet, resync on next start byte
                        self.get_logger().info('Error on Packet Read!')
                        continue

                    steer_cmd = data[0]
                    throttle_u8 = data[1]
                    brake_u8 = data[2]

                    # Clamp to expected ranges
                    steer_cmd = max(0, min(127, steer_cmd))
                    throttle_u8 = max(0, min(255, throttle_u8))
                    brake_u8 = max(0, min(255, brake_u8))

                    self.steering_motor_cmd = steer_cmd
                    self.throttle_cmd_u = throttle_u8 / 255.0
                    self.brake_cmd_u = brake_u8 / 255.0

                    self.get_logger().info(
                        f'RX <- Steer cmd: {steer_cmd} (0-127), '
                        f'Throttle: {self.throttle_cmd_u:.2f}, '
                        f'Brake: {self.brake_cmd_u:.2f}',
                        throttle_duration_sec=1.0,
                    )

                    # Publish to effort controllers
                    self._publish_motor_commands()
                #else:
                # Unknown packet ID, ignore for now
                   # self.get_logger().warn(
                   #     f'Unknown packet ID: {packet_id}',
                   #     #throttle_duration_sec=5.0,
                   # )

            except serial.SerialException as e:
                self.get_logger().error(f'Serial read error: {e}')
                self.serial_connected = False
                break

    def _publish_motor_commands(self) -> None:
        """Convert C2000 motor commands to joint efforts and publish.

        - Steering maps Sabertooth 0-127 to a normalized -1..1 command.
        - Throttle (0-1) produces forward drive torque only.
        - Brake (0-1) produces torque that always opposes wheel motion
          and never drives the cart into reverse.
        """
        # --- Steering: Sabertooth 0-127 -> normalized -1..1 ---
        if self.steering_motor_cmd < 64:
            # Reverse: 0 maps to -100%, 63 maps to ~0%
            steering_normalized = (self.steering_motor_cmd - 64) / 64.0
        elif self.steering_motor_cmd == 64:
            steering_normalized = 0.0
        else:
            # Forward: 65 maps to ~0%, 127 maps to +100%
            steering_normalized = (self.steering_motor_cmd - 64) / 63.0

        # Clamp steering to sane range
        steering_normalized = max(-1.0, min(1.0, steering_normalized))
        steering_effort = steering_normalized * self.steering_max_torque

        # --- Throttle & brake: normalized 0-1 ---
        throttle_norm = max(0.0, min(1.0, self.throttle_cmd_u))
        brake_norm = max(0.0, min(1.0, self.brake_cmd_u))

        # Drive torque: forward only
        T_drive = throttle_norm * self.drive_max_torque

        # Brake torque: always opposes current wheel motion and
        # is disabled near zero speed to avoid "braking into reverse"
        omega = self.drive_velocity             # rad/s
        vel_eps = self.brake_velocity_threshold

        if abs(omega) > vel_eps and brake_norm > 0.0:
            # Oppose the current direction of motion
            T_brake = -math.copysign(brake_norm * self.brake_max_torque, omega)
        else:
            T_brake = 0.0

        T_total = T_drive + T_brake

        # Publish steering command
        steering_msg = Float64MultiArray()
        steering_msg.data = [steering_effort]
        self.steering_cmd_pub.publish(steering_msg)

        # Publish drive command (both rear wheels)
        drive_msg = Float64MultiArray()
        drive_msg.data = [T_total, T_total]
        self.drive_cmd_pub.publish(drive_msg)

    def timer_callback(self) -> None:
        """Periodic callback to send sensor data and log state."""
        # Send encoder counts to C2000
        self._send_sensor_data()

        # Log current state periodically
        #if self.serial_connected:
        #    self.get_logger().debug(
        #        f'State - Steer enc: {self.steering_encoder_counts}, '
        #        f'Drive enc: {self.drive_encoder_counts}, '
        #        f'Steer cmd: {self.steering_motor_cmd} (0-127), '
        #        f'Throttle: {self.throttle_cmd_u:.2f}, Brake: {self.brake_cmd_u:.2f}',
        #        #throttle_duration_sec=2.0,
        #    )

    def send_test_command(self, steering_effort: float = 0.0, drive_effort: float = 0.0) -> None:
        """Helper function to send test commands directly to the effort controllers."""
        # Steering command
        steering_msg = Float64MultiArray()
        steering_msg.data = [steering_effort]
        self.steering_cmd_pub.publish(steering_msg)

        # Drive command (both rear wheels)
        drive_msg = Float64MultiArray()
        drive_msg.data = [drive_effort, drive_effort]
        self.drive_cmd_pub.publish(drive_msg)

        self.get_logger().info(
            f'Sent test commands - Steering: {steering_effort}, Drive: {drive_effort}'
        )

    def destroy_node(self) -> None:
        """Cleanup on shutdown."""
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        # Best-effort join on receive thread
        if hasattr(self, 'receive_thread') and self.receive_thread is not None:
            if self.receive_thread.is_alive():
                self.receive_thread.join(timeout=0.2)
        super().destroy_node()


def main(args=None) -> None:
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

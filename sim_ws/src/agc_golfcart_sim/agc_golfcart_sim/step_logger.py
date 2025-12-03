#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
import csv
import os


class ControllerLogger(Node):
    def __init__(self):
        super().__init__('controller_logger')

        # --- Parameters ---
        self.declare_parameter('joint_states_topic', '/joint_states')
        self.declare_parameter('drive_joint_name', 'rear_left_wheel_joint')
        self.declare_parameter('steering_joint_name', 'steering_input_joint')
        self.declare_parameter('wheel_radius', 0.292)      # [m]
        self.declare_parameter('csv_path', 'controller_log.csv')

        self.declare_parameter('drive_cmd_topic', '/rear_drive_controller/commands')
        self.declare_parameter('steer_cmd_topic', '/steering_controller/commands')

        js_topic = self.get_parameter('joint_states_topic').get_parameter_value().string_value
        self.drive_joint = self.get_parameter('drive_joint_name').get_parameter_value().string_value
        self.steer_joint = self.get_parameter('steering_joint_name').get_parameter_value().string_value
        self.r = self.get_parameter('wheel_radius').get_parameter_value().double_value
        csv_path = self.get_parameter('csv_path').get_parameter_value().string_value
        drive_cmd_topic = self.get_parameter('drive_cmd_topic').get_parameter_value().string_value
        steer_cmd_topic = self.get_parameter('steer_cmd_topic').get_parameter_value().string_value

        self.get_logger().info(f'Listening to joint states: {js_topic}')
        self.get_logger().info(f'Drive joint: {self.drive_joint}')
        self.get_logger().info(f'Steering joint: {self.steer_joint}')
        self.get_logger().info(f'Wheel radius: {self.r} m')
        self.get_logger().info(f'Drive cmd topic: {drive_cmd_topic}')
        self.get_logger().info(f'Steer cmd topic: {steer_cmd_topic}')
        self.get_logger().info(f'Writing CSV: {os.path.abspath(csv_path)}')

        # Time base (sim time)
        self.t0 = None

        # Latest commands
        self.last_drive_cmd = [0.0, 0.0]   # [left, right] or [0,0]
        self.last_steer_cmd = 0.0          # single effort value

        # Open CSV
        self.csv_file = open(csv_path, 'w', newline='')
        self.writer = csv.writer(self.csv_file)
        # Columns:
        # t, v_meas, steering_angle, drive_cmd_0, drive_cmd_1, steer_cmd
        self.writer.writerow([
            't_sim_sec',
            'v_meas_mps',
            'steering_angle_rad',
            'drive_cmd_0',
            'drive_cmd_1',
            'steer_cmd'
        ])

        # Subscribers
        self.sub_js = self.create_subscription(
            JointState, js_topic, self.joint_states_cb, 50
        )
        self.sub_drive = self.create_subscription(
            Float64MultiArray, drive_cmd_topic, self.drive_cmd_cb, 10
        )
        self.sub_steer = self.create_subscription(
            Float64MultiArray, steer_cmd_topic, self.steer_cmd_cb, 10
        )

    # --- Callbacks ---

    def drive_cmd_cb(self, msg: Float64MultiArray):
        # rear_drive_controller/commands usually has 2 entries [left, right]
        if len(msg.data) >= 2:
            self.last_drive_cmd = [msg.data[0], msg.data[1]]
        elif len(msg.data) == 1:
            self.last_drive_cmd = [msg.data[0], msg.data[0]]
        else:
            self.last_drive_cmd = [0.0, 0.0]

    def steer_cmd_cb(self, msg: Float64MultiArray):
        # steering_controller/commands typically has 1 entry [effort]
        if len(msg.data) >= 1:
            self.last_steer_cmd = msg.data[0]
        else:
            self.last_steer_cmd = 0.0

    def joint_states_cb(self, msg: JointState):
        # Sim time from header
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if self.t0 is None:
            self.t0 = t
        t_rel = t - self.t0

        # Build name -> index map once per message
        name_to_idx = {name: i for i, name in enumerate(msg.name)}

        # --- Longitudinal speed from drive joint ---
        v_meas = 0.0
        if self.drive_joint in name_to_idx and name_to_idx[self.drive_joint] < len(msg.velocity):
            omega = msg.velocity[name_to_idx[self.drive_joint]]  # rad/s
            v_meas = omega * self.r                              # m/s

        # --- Steering angle from steering joint ---
        steering_angle = 0.0
        if self.steer_joint in name_to_idx and name_to_idx[self.steer_joint] < len(msg.position):
            steering_angle = msg.position[name_to_idx[self.steer_joint]]

        # Write row
        self.writer.writerow([
            t_rel,
            v_meas,
            steering_angle,
            self.last_drive_cmd[0],
            self.last_drive_cmd[1],
            self.last_steer_cmd
        ])

        # Flush so you don't lose data when you ctrl+c
        self.csv_file.flush()

    def destroy_node(self):
        self.get_logger().info('Closing CSV file')
        try:
            self.csv_file.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ControllerLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

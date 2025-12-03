#!/usr/bin/env python3
import csv
import sys
import matplotlib.pyplot as plt


def load_speed_log(path):
    t = []
    v = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            t.append(float(row['t_sim_sec']))
            v.append(float(row['v_meas_mps']))
    return t, v


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 plot_speed_log.py speed_log.csv")
        sys.exit(1)

    path = sys.argv[1]
    t, v = load_speed_log(path)

    plt.figure()
    plt.plot(t, v, linewidth=1.5)
    plt.grid(True)
    plt.xlabel('Simulation Time [s]')
    plt.ylabel('Speed [m/s]')
    plt.title('Speed vs Time from Gazebo (/joint_states)')
    plt.show()


if __name__ == '__main__':
    main()

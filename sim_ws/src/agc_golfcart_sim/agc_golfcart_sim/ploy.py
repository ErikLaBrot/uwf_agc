import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
# ------------------------------------------------------------------
# User settings – tweak these for your log
# ------------------------------------------------------------------
SPEED_FILE = "controller_log_speed_brake.csv"
STEER_FILE = "controller_log_steer.csv"

# Speed / brake step times (seconds)
# These are good for the log you sent; adjust as needed
ACCEL_STEP_TIME = 5.44    # when drive_cmd_0 first steps up
ACCEL_PRE       = 0.5     # seconds before step to include
ACCEL_POST      = 18.0    # seconds after step to include

BRAKE_STEP_TIME = 24.0    # when sustained braking starts
BRAKE_PRE       = 0.5
BRAKE_POST      = 11.0

# Steering step time
STEER_STEP_TIME = 9.77    # first big steering command
STEER_PRE       = 0.5
STEER_POST      = 2.5     # short so we stay in the first steering “loop”

# Low-pass time constants for filtering (for plotting + metrics)
TAU_SPEED = 0.3           # s, speed filter
TAU_STEER = 0.0          # s, steering angle filter

# Command values for error calculations
V_CMD_ACCEL = 5.0         # m/s, set to whatever speed you actually commanded
V_CMD_BRAKE = 0.0         # m/s, braking to a stop

# If None, rotations->radians will be estimated from log
STEER_ROT_TO_RAD = None   # rad per rotation of steer_cmd

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def lowpass_iir(x, t, tau):
    """Simple first order low pass, x, t same length, tau in seconds"""
    x = np.asarray(x, dtype=float)
    t = np.asarray(t, dtype=float)
    y = np.zeros_like(x)
    y[0] = x[0]
    for k in range(1, len(x)):
        dt = t[k] - t[k-1]
        if dt <= 0:
            alpha = 0.0
        else:
            alpha = np.exp(-dt / tau)
        y[k] = alpha * y[k-1] + (1 - alpha) * x[k]
    return y


def compute_step_metrics(t, y, y_cmd, steady_window=1.0,
                         frac_low=0.1, frac_high=0.9):
    """
    Generic step metrics, supports up or down steps
    t: time array, preferably with t=0 at command step
    y: output signal
    y_cmd: commanded final value
    steady_window: seconds at the end used for steady state average
    Returns dict: rise_time, t_10, t_90, y_ss, ss_error
    """
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)

    y0 = y[0]
    A = y_cmd - y0
    if A == 0:
        return {
            "rise_time": np.nan,
            "t_10": np.nan,
            "t_90": np.nan,
            "y_ss": y0,
            "ss_error": 0.0,
        }

    # 10% and 90% levels along the step from y0 -> y_cmd
    y10 = y0 + frac_low * A
    y90 = y0 + frac_high * A

    def first_cross(target):
        if A > 0:
            idx = np.where(y >= target)[0]
        else:
            idx = np.where(y <= target)[0]
        if len(idx) == 0:
            return np.nan
        return t[idx[0]]

    t10 = first_cross(y10)
    t90 = first_cross(y90)
    rise = t90 - t10 if (np.isfinite(t90) and np.isfinite(t10)) else np.nan

    # steady state from last steady_window seconds
    t_end = t[-1]
    mask_ss = t >= (t_end - steady_window)
    y_ss = np.mean(y[mask_ss]) if np.any(mask_ss) else y[-1]
    ss_error = y_ss - y_cmd

    return {
        "rise_time": float(rise),
        "t_10": float(t10),
        "t_90": float(t90),
        "y_ss": float(y_ss),
        "ss_error": float(ss_error),
    }

# ------------------------------------------------------------------
# Load logs
# ------------------------------------------------------------------
speed_df = pd.read_csv(SPEED_FILE)
steer_df = pd.read_csv(STEER_FILE)

# ------------------------------------------------------------------
# 1) Accel step: speed vs time (raw + filtered, time-shifted)
# ------------------------------------------------------------------
t = speed_df["t_sim_sec"].values
v = speed_df["v_meas_mps"].values

mask_accel = (t >= ACCEL_STEP_TIME - ACCEL_PRE) & (t <= ACCEL_STEP_TIME + ACCEL_POST)
t_accel = t[mask_accel]
v_accel = v[mask_accel]
t_accel_shift = t_accel - ACCEL_STEP_TIME

v_accel_filt = lowpass_iir(v_accel, t_accel, tau=TAU_SPEED)

metrics_accel = compute_step_metrics(
    t_accel_shift, v_accel_filt, V_CMD_ACCEL, steady_window=2.0
)

print("\n=== Accel step metrics ===")
for k, val in metrics_accel.items():
    print(f"{k:10s}: {val: .4f}")

plt.figure()
plt.plot(t_accel_shift, v_accel, label="raw")
#plt.plot(t_accel_shift, v_accel_filt, label="filtered")
plt.axhline(V_CMD_ACCEL, linestyle="--", label="v_cmd")
plt.xlabel("Time since accel step [s]")
plt.ylabel("Speed v_meas_mps [m/s]")
plt.title("Acceleration step response")
plt.grid(True)
plt.legend()
plt.tight_layout()

# ------------------------------------------------------------------
# 2) Brake step: speed vs time (raw + filtered, time-shifted)
# ------------------------------------------------------------------
mask_brake = (t >= BRAKE_STEP_TIME - BRAKE_PRE) & (t <= BRAKE_STEP_TIME + BRAKE_POST)
t_brake = t[mask_brake]
v_brake = v[mask_brake]
t_brake_shift = t_brake - BRAKE_STEP_TIME

v_brake_filt = lowpass_iir(v_brake, t_brake, tau=TAU_SPEED)

metrics_brake = compute_step_metrics(
    t_brake_shift, v_brake_filt, V_CMD_BRAKE, steady_window=2.0
)

print("\n=== Brake step metrics ===")
for k, val in metrics_brake.items():
    print(f"{k:10s}: {val: .4f}")

plt.figure()
plt.plot(t_brake_shift, v_brake, label="raw")
#plt.plot(t_brake_shift, v_brake_filt, label="filtered")
plt.axhline(V_CMD_BRAKE, linestyle="--", label="v_cmd")
plt.xlabel("Time since brake step [s]")
plt.ylabel("Speed v_meas_mps [m/s]")
plt.title("Brake step response")
plt.grid(True)
plt.legend()
plt.tight_layout()

# ------------------------------------------------------------------
# 3) Steering step: angle vs time (raw + filtered, time-shifted)
# ------------------------------------------------------------------
s_t     = steer_df["t_sim_sec"].values
s_theta = steer_df["steering_angle_rad"].values     # measured joint angle [rad]
s_cmd   = steer_df["steer_cmd"].values              # command in *rotations* of steering column

# Explicit mapping: 3.5 rotations of column -> 45 deg (pi/4 rad) at wheel,
# so steering ratio = 28:1 and 1 rotation -> pi/14 rad at the joint.
if STEER_ROT_TO_RAD is None:
    STEER_ROT_TO_RAD = math.pi / 3.5   # rad per rotation of steering column

mask_steer = (s_t >= STEER_STEP_TIME - STEER_PRE) & (s_t <= STEER_STEP_TIME + STEER_POST)
t_steer        = s_t[mask_steer]
theta          = s_theta[mask_steer]
cmd_rot_window = s_cmd[mask_steer]                     # rotations
t_steer_shift  = t_steer - STEER_STEP_TIME

# Convert command from rotations -> joint radians over the whole window
theta_cmd_window = cmd_rot_window * STEER_ROT_TO_RAD   # [rad]

# Filter measured angle for cleaner metrics/plot
theta_filt = lowpass_iir(theta, t_steer, tau=TAU_STEER)

# Commanded joint angle based on step value at STEER_STEP_TIME
idx_step      = np.argmin(np.abs(s_t - STEER_STEP_TIME))
cmd_rot_step  = s_cmd[idx_step]              # [rotations]
theta_cmd_rad = cmd_rot_step * STEER_ROT_TO_RAD

metrics_steer = compute_step_metrics(
    t_steer_shift, theta_filt, theta_cmd_rad, steady_window=0.5
)

print("\n=== Steering step metrics ===")
print(f"STEER_ROT_TO_RAD (explicit) = {STEER_ROT_TO_RAD:.6f} rad/rotation")
print(f"cmd_rot_step = {cmd_rot_step:.4f} rotations, theta_cmd_rad = {theta_cmd_rad:.4f} rad")
for k, val in metrics_steer.items():
    print(f"{k:10s}: {val: .4f}")

plt.figure()
plt.plot(t_steer_shift, theta,         label="raw angle [rad]")
#plt.plot(t_steer_shift, theta_filt,    label="filtered angle [rad]")
plt.plot(t_steer_shift, theta_cmd_window, "--", label="command [rad]")
plt.xlabel("Time since steering step [s]")
plt.ylabel("Steering angle [rad]")
plt.title("Steering step response")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.show()

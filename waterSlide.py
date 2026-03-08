import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation

# Physics Constants
g = 9.81 

def calculate_physics(mu_k, t_total, v0, theta_deg):
    theta = np.radians(theta_deg)
    # a = g(sinθ - μ cosθ)
    accel = g * (np.sin(theta) - mu_k * np.cos(theta))
    accel = max(0, accel)
    
    # Total distance d = v0*t + 0.5*a*t^2
    total_dist = v0 * t_total + 0.5 * accel * (t_total**2)
    height = total_dist * np.sin(theta)
    width = total_dist * np.cos(theta)
    return total_dist, height, width, accel, theta

# Setup Figure
fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(bottom=0.35, top=0.85, right=0.8) # Adjusted right margin for the button

# Sliders
s_mu = Slider(plt.axes([0.2, 0.2, 0.55, 0.03]), 'Friction (μ)', 0.0, 0.5, valinit=0.05, valstep=0.01)
s_time = Slider(plt.axes([0.2, 0.15, 0.55, 0.03]), 'Ride Time (s)', 1, 30, valinit=15, valstep=1)
s_v0_kph = Slider(plt.axes([0.2, 0.1, 0.55, 0.03]), 'Start Speed (km/h)', 0, 45, valinit=0, valstep=1)
s_angle = Slider(plt.axes([0.2, 0.05, 0.55, 0.03]), 'Angle (°)', 1, 45, valinit=10, valstep=1)

# Drawing Elements
slide_line, = ax.plot([], [], 'b-', lw=4)
ground_line, = ax.plot([], [], 'k--', alpha=0.3)
rider, = ax.plot([], [], 'ro', markersize=15, label="Rider") 

# Logic to handle the play/pause state and resets
class AnimationState:
    def __init__(self):
        self.physics_frame = 0
        self.is_playing = False

    def reset(self, event=None):
        # Whenever a slider moves, bring the rider back to the top
        self.physics_frame = 0

    def toggle_play(self, event):
        self.is_playing = not self.is_playing
        if self.is_playing:
            btn_start.label.set_text('Pause')
            btn_start.color = 'lightcoral'
        else:
            btn_start.label.set_text('Start')
            btn_start.color = 'lightgreen'
        fig.canvas.draw_idle()

state = AnimationState()

# Attach reset trigger to all sliders
s_mu.on_changed(state.reset)
s_time.on_changed(state.reset)
s_v0_kph.on_changed(state.reset)
s_angle.on_changed(state.reset)

# Create the Big Start Button
ax_btn = plt.axes([0.8, 0.08, 0.15, 0.1]) # [left, bottom, width, height]
btn_start = Button(ax_btn, 'Start', color='lightgreen', hovercolor='palegreen')
btn_start.on_clicked(state.toggle_play)
btn_start.label.set_fontsize(14)
btn_start.label.set_fontweight('bold')

def update(frame):
    # Only advance the rider's time if the simulation is playing
    if state.is_playing:
        state.physics_frame += 1
        
    # Current slider values
    mu = s_mu.val
    t_target = s_time.val
    v0 = s_v0_kph.val / 3.6  # Convert km/h to m/s
    theta_deg = s_angle.val
    
    # Physics Calculations
    L_total, H, W, A, theta = calculate_physics(mu, t_target, v0, theta_deg)
    
    # Time logic (looping)
    current_t = (state.physics_frame * 0.05) % t_target
    
    # If the time loops back, pause the animation automatically? (Optional)
    # Uncomment the next lines if you want it to stop at the bottom instead of looping infinitely:
    # if current_t < ((state.physics_frame - 1) * 0.05) % t_target:
    #     state.toggle_play(None) 
    
    # Position at current time
    d_current = v0 * current_t + 0.5 * A * (current_t**2)
    
    # Coordinate Mapping
    curr_x = d_current * np.cos(theta)
    curr_y = H - (d_current * np.sin(theta))
    
    # Update Graphics
    slide_line.set_data([0, W], [H, 0])
    ground_line.set_data([0, W], [0, 0])
    rider.set_data([curr_x], [curr_y])
    
    # Dynamic Axis Scaling
    ax.set_xlim(-5, max(W, 20) + 10)
    ax.set_ylim(-5, max(H, 20) + 10)
    
    # Update Stats
    current_speed = v0 + A * current_t
    current_speed_kph = current_speed * 3.6
    fig.suptitle(f"SLIDE HEIGHT: {H:.2f}m   |   SLIDE LENGTH: {L_total:.2f}m\n"
                 f"Current Speed: {current_speed_kph:.1f} km/h  |  Time: {current_t:.1f}s / {t_target:.1f}s", 
                 fontsize=12, fontweight='bold')
    
    return slide_line, rider, ground_line

ani = FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)

plt.show()

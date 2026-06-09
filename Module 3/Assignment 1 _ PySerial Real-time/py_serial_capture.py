import serial
import csv
import time
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# --- CONFIGURATION ---
SERIAL_PORT = 'COM5'    # Windows: 'COM3', Mac/Linux: '/dev/ttyUSB0'
BAUD_RATE = 115200      # Must match ESP32
CSV_FILENAME = 'sensor_log.csv'
PLOT_WINDOW = 100       # How many data points to show on screen (Rolling window)

# --- GLOBAL VARIABLES ---
# Deque is a fast list optimized for appends and pops from ends
data_buffer = deque(maxlen=PLOT_WINDOW) 
time_buffer = deque(maxlen=PLOT_WINDOW)
is_running = True

def read_serial_and_log():
    """
    Background thread: Reads serial data, logs to CSV, update plot buffer.
    """
    global is_running
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
        
        # Initialize CSV
        with open(CSV_FILENAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "SensorValue"]) # Header
            
            print("Logging started. Press Ctrl+C in terminal to stop.")
            
            while is_running:
                if ser.in_waiting > 0:
                    try:
                        # Read line, decode bytes to string, strip whitespace
                        line = ser.readline().decode('utf-8').strip()
                        
                        # Skip empty lines
                        if not line: continue

                        # Parse data (Assuming ESP32 sends a single number per line)
                        # If sending "val1, val2", use line.split(',')
                        value = float(line)
                        current_time = time.time()
                        
                        # 1. Write to CSV (Persistent Storage)
                        writer.writerow([current_time, value])
                        
                        # 2. Update Plot Buffer (Visualization)
                        data_buffer.append(value)
                        time_buffer.append(current_time)
                        
                    except ValueError:
                        # Handle cases where serial data is corrupted/incomplete
                        pass
                        
    except serial.SerialException as e:
        print(f"Error connecting to serial port: {e}")
        is_running = False

def update_plot(frame, line_plot, ax):
    """
    Called by Matplotlib animation to update the chart.
    """
    if len(data_buffer) > 0:
        # Update the data in the plot
        line_plot.set_data(range(len(data_buffer)), data_buffer)
        
        # Dynamic Axis Adjustment
        ax.set_xlim(0, PLOT_WINDOW)
        ax.set_ylim(min(data_buffer) - 1, max(data_buffer) + 1)
        
    return line_plot,

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Start the Serial/CSV Thread
    thread = threading.Thread(target=read_serial_and_log)
    thread.daemon = True # Ensures thread dies when main program dies
    thread.start()

    # 2. Setup Plotting (Must be in main thread)
    fig, ax = plt.subplots()
    ax.set_title(f"Real-Time ESP32 Data ({BAUD_RATE} Baud)")
    ax.set_xlabel("Samples (Rolling Window)")
    ax.set_ylabel("Sensor Value")
    
    # Initialize an empty line
    line_plot, = ax.plot([], [], 'r-', lw=2) 
    
    # 3. Start Animation
    # Interval=50ms means it refreshes at 20FPS. 
    # This is independent of the incoming data rate.
    ani = animation.FuncAnimation(fig, update_plot, fargs=(line_plot, ax), 
                                  interval=50, blit=False, cache_frame_data=False)

    try:
        plt.show()
    except KeyboardInterrupt:
        is_running = False
        print("Stopping...")
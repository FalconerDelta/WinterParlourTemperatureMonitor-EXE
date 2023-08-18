import requests
import winsound
import time
import tkinter as tk
from tkinter import messagebox, ttk

class WinterParlourTemperatureMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Winter Parlour Temperature Monitor")

        self.json_url = "https://reg.bom.gov.au/fwo/IDV60901/IDV60901.94866.json"
        self.previous_temperature = 100
        self.below_5_beep_played = False
        self.between_5_10_beep_played = False
        self.check_interval = tk.StringVar(value="5")  # Default interval in minutes
        self.temperature_value = tk.StringVar(value="-")

        self.temperature_label = tk.Label(self.root, text="Temperature:")
        self.temperature_label.pack()

        self.temperature_display = tk.Label(self.root, textvariable=self.temperature_value)
        self.temperature_display.pack()

        self.status_label = tk.Label(self.root, text="Status:")
        self.status_label.pack()

        self.interval_label = tk.Label(self.root, text="Check Interval (minutes):")
        self.interval_label.pack()

        self.interval_entry = tk.Entry(self.root, textvariable=self.check_interval)
        self.interval_entry.pack()

        self.start_button = tk.Button(self.root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack()

        self.stop_button = tk.Button(self.root, text="Stop Monitoring", command=self.stop_monitoring)
        self.stop_button.pack()
        self.stop_button.config(state=tk.DISABLED)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set the window size
        self.root.geometry("400x300")  # You can adjust the dimensions as needed

    def start_monitoring(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_temperature()

    def stop_monitoring(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def update_temperature(self):
        try:
            response = requests.get(self.json_url)
            data = response.json()
            temperature = data['observations']['data'][0]['air_temp']

            if temperature is not None:
                temperature = float(temperature)
                self.temperature_value.set(f"{temperature} °C")

                if temperature != self.previous_temperature:
                    if temperature <= 5:
                        if not self.below_5_beep_played:
                            self.play_sound(2)
                            self.below_5_beep_played = True
                            self.between_5_10_beep_played = False
                            self.update_status("Temperature is 5 degrees or below.")
                    elif 5 < temperature <= 10:
                        if not self.between_5_10_beep_played:
                            self.play_sound(1)
                            self.between_5_10_beep_played = True
                            self.below_5_beep_played = False
                            self.update_status("Temperature is between 5 and 10 degrees.")
                    else:
                        self.below_5_beep_played = False
                        self.between_5_10_beep_played = False
                        self.update_status("Temperature is above 10 degrees.")

                    self.previous_temperature = temperature

            interval_minutes = int(self.check_interval.get())
            self.root.after(interval_minutes * 60000, self.update_temperature)

        except Exception as e:
            self.update_status("An error occurred: " + str(e))

    def play_sound(self, num_beeps):
        for _ in range(num_beeps):
            winsound.Beep(1000, 1000)  # Frequency: 1000 Hz, Duration: 1000 ms

    def update_status(self, status_text):
        self.status_label.config(text="Status: " + status_text)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WinterParlourTemperatureMonitorApp(root)
    root.mainloop()

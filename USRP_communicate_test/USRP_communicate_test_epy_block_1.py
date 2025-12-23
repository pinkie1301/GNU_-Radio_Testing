import numpy as np
from gnuradio import gr
import datetime
import csv

class noise_logger(gr.sync_block):
    """
    This block calculates the average noise power, excluding peaks, and logs it to a CSV file.
    
    Input: Vector of power spectrum values (float).
    Output: None.
    """
    def __init__(self, samp_rate=2e6, fft_size=1024, trim_percent=0.1, log_interval=1.0, filename="rx_noise_log.csv"):
        gr.sync_block.__init__(
            self,
            name='Noise Logger',
            in_sig=[(np.float32, fft_size)],
            out_sig=[]
        )
        self.fft_size = int(fft_size)
        self.samp_rate = float(samp_rate)
        self.trim_count = int(self.fft_size * trim_percent) # Number of top bins to exclude
        self.log_interval = float(log_interval) # Log interval in seconds
        self.filename = filename

        # Calculate how many FFT vectors represent the logging interval
        # If log_interval is 0.5s, we need half as many vectors as 1s
        self.vectors_per_interval = int((self.samp_rate / self.fft_size) * self.log_interval)
        
        # Safety check: ensure at least 1 vector is processed
        if self.vectors_per_interval < 1:
             self.vectors_per_interval = 1

        self.vector_counter = 0
        self.power_buffer = []

        # Open the file and write the header
        self.csvfile = open(self.filename, 'w', newline='')
        self.writer = csv.writer(self.csvfile)
        self.writer.writerow(['time_stamp', 'noise_floor_db']) # Updated header name

    def stop(self):
        # Ensure the file is closed when the flowgraph stops
        self.csvfile.close()

    def work(self, input_items, output_items):
        # input_items[0] is a list of input vectors. We process them one by one.
        for vector in input_items[0]:
            # 1. Sort the power values in ascending order
            sorted_power = np.sort(vector)

            # 2. Exclude the top 'trim_count' bins (the peaks)
            # We also exclude the lowest bin which can sometimes be the DC offset
            noise_bins = sorted_power[1:-self.trim_count]

            # 3. Calculate the average of the remaining noise bins
            if len(noise_bins) > 0:
                avg_noise_power = np.mean(noise_bins)
                self.power_buffer.append(avg_noise_power)

            self.vector_counter += 1

            # 4. Check if enough vectors have been processed for the interval
            if self.vector_counter >= self.vectors_per_interval:
                if len(self.power_buffer) > 0:
                    # Calculate the average over the interval
                    interval_avg_power = np.mean(self.power_buffer)

                    # Normalize the power (divide by FFT size squared) to match Frequency Sink
                    normalized_power = interval_avg_power / (self.fft_size ** 2)
                    
                    # Convert to relative dB (Noise Floor)
                    # Add small epsilon to prevent log(0)
                    noise_db_relative = 10 * np.log10(normalized_power + 1e-20)
                    
                    # Get timestamp and write to file
                    timestamp = datetime.datetime.now().isoformat()
                    
                    # Write the CORRECT normalized value
                    self.writer.writerow([timestamp, f"{noise_db_relative:.2f}"])
                    self.csvfile.flush() # Ensure it's written immediately

                # Reset for the next interval
                self.vector_counter = 0
                self.power_buffer = []

        return len(input_items[0])

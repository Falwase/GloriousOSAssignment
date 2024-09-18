import matplotlib.pyplot as plt
import subprocess
import os
import numpy as np
from scipy.interpolate import PchipInterpolator
import json

def save_plot(data, result_path):
    plt.figure(figsize=(12, 8))
    for alg, hit_rates in data.items():
        frame_counts = np.array(list(hit_rates.keys()))
        hit_rates_values = np.array(list(hit_rates.values()))
        
        # Sort the data points
        sort_idx = np.argsort(frame_counts)
        x = frame_counts[sort_idx]
        y = hit_rates_values[sort_idx]

        # Create PchipInterpolator
        pchip = PchipInterpolator(x, y, extrapolate=True)
        
        # Generate points for smooth curve
        x_smooth = np.linspace(x.min(), x.max(), 300)
        y_smooth = pchip(x_smooth)
        
        plt.plot(x_smooth, y_smooth, label=alg)
        plt.scatter(x, y, alpha=0.5)

    plt.grid(True)
    plt.legend()
    plt.xlabel('Frame Count')
    plt.ylabel('Hit Rate')
    plt.title('Algorithm Performance: Hit Rate vs Frame Count')
    #plt.xlim(0, 10)  # Set x-axis limits
    #plt.ylim(0.2, 1.0)  # Set y-axis limits
    plt.savefig(result_path, dpi=300, bbox_inches='tight')
    plt.close()

def save_results(data, result_path):
    json_object = json.dumps(data, indent = 4)
    with open(result_path, 'w') as write_file:
        write_file.write(json_object)

def record_trace_memory_use(write_path, trace_files):
    write_path = os.path.join(write_path, "test.txt")
    trace_memory_use = {}
    for trace_file in trace_files:
        requested_addresses = set()
        with open(trace_file, 'r') as trace:
            for trace_line in trace:
                trace_line = trace_line.split(" ")
                if trace_line[0] not in requested_addresses:
                    requested_addresses.add(trace_line[0])
        trace_memory_use[trace_file] = len(requested_addresses)

    with open(write_path, 'w') as write_file:
        write_file.write(json.dumps(trace_memory_use))
    
def main():
    debug_mode = "quiet"
    
    # Command Arguments
    trace_files = ["gcc.trace", "sixpack.trace", "swim.trace", "bzip.trace"]
    frame_counts = ["1","3","6","9", "12", "15"]
    page_replace_algs = ["rand", "lru", "clock"]
    result_folder = "results"
    alg_hit_rates = {}
    
    # Run each algorithm on the specified trace with all frame counts and store the results
    for trace in trace_files:
        for alg in page_replace_algs:
            hit_rates = {}
            for frame_count in frame_counts:
                print(f"\rRunning {trace} with {alg} for a frame count of {frame_count}.      ", end="")
                # Run Algorithm
                command = ["python3", "memsim.py", trace, frame_count, alg, debug_mode]
                result = subprocess.run(command, capture_output=True, text=True)
                #print(f"--------------------------\n{result}\n--------------------------")
                
                # Store Results
                result = result.stdout.strip().split('\n')
                event_count = int(result[1].split(" ")[-1])
                disk_read_count = int(result[2].split(" ")[-1])
                disk_write_count = int(result[3].split(" ")[-1])
                page_fault_rate = float(result[4].split(" ")[-1])
                hit_rates[int(frame_count)] = 1.0-page_fault_rate
                
            alg_hit_rates[alg] = hit_rates
            
        plot_path = os.path.join(result_folder, f"{trace}.png")
        result_path = os.path.join(result_folder, f"{trace}.txt")
        save_plot(alg_hit_rates, plot_path)
        if True:
            save_results(alg_hit_rates, result_path)

    if True:
        record_trace_memory_use(result_folder, trace_files)

if __name__ == "__main__":
    main()

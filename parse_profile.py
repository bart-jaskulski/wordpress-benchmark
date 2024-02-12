import re
from collections import defaultdict
from statistics import mean, median, stdev

# Function to calculate statistics or return placeholders if not enough data
def calculate_stats(values):
    if len(values) < 2:
        # If less than two data points, return placeholders
        return (mean(values), median(values), "N/A") if values else (0, 0, "N/A")
    else:
        # Calculate statistics normally
        return (mean(values), median(values), round(stdev(values), 2))

def calculate_percentage_diff(value_a, value_b):
    if value_a == 0:
        return "N/A"
    return round(((value_b - value_a) / value_a) * 100, 2)

# Function to parse the input data and extract the relevant stats
def parse_input(input_lines):
    wall_times = defaultdict(list)
    memory_usages = defaultdict(list)

    for line in input_lines:
        if line.startswith('File:'):
            file_data = line.split(': ')[1]
            request_type, _, build = re.search(r'(\w+)\.(\w+)\.(\w+)\.xhprof', file_data).groups()
            group = f"{request_type}.{build}"
        elif 'main()' in line:
            parts = line.split()
            wall_time = float(parts[1][:-2])
            memory_usage = float(parts[7][:-1])
            wall_times[group].append(wall_time)
            memory_usages[group].append(memory_usage)

    return wall_times, memory_usages

# Function to generate markdown tables
def generate_markdown_tables(wall_times, memory_usages):
    builds = ['trunk', 'autoload'] # sorted(set(group.split('.')[1] for group in wall_times.keys()))
    request_types = sorted(set(group.split('.')[0] for group in wall_times.keys()))
    diff_column = "Percentage Diff"

    wall_time_rows = ["|                          | " + " | ".join(builds + [diff_column]) + " |"]
    memory_usage_rows = ["|                          | " + " | ".join(builds + [diff_column]) + " |"]

    wall_time_rows.append("|--------------------------|" + "|".join(["--------------"] * (len(builds) + 1)) + "|")
    memory_usage_rows.append("|--------------------------|" + "|".join(["---------"] * (len(builds) + 1)) + "|")

    for r_type in request_types:
        # We know that we have two builds "trunk" and "autoload"
        trunk_stats = calculate_stats(wall_times.get(f'{r_type}.trunk', []))
        autoload_stats = calculate_stats(wall_times.get(f'{r_type}.autoload', []))
        percent_diff_time = calculate_percentage_diff(trunk_stats[0], autoload_stats[0])

        w_times = [
            "{:.2f}ms / {:.2f}ms / ±{:.2f}".format(*trunk_stats),
            "{:.2f}ms / {:.2f}ms / ±{:.2f}".format(*autoload_stats),
            "{}%".format(percent_diff_time)
        ]

        trunk_stats = calculate_stats(memory_usages.get(f'{r_type}.trunk', []))
        autoload_stats = calculate_stats(memory_usages.get(f'{r_type}.autoload', []))
        percent_diff_mem = calculate_percentage_diff(trunk_stats[0], autoload_stats[0])

        m_usages = [
            "{:.2f}M / {:.2f}M / ±{:.2f}".format(*trunk_stats),
            "{:.2f}M / {:.2f}M / ±{:.2f}".format(*autoload_stats),
            "{}%".format(percent_diff_mem)
        ]

        wall_time_rows.append(f"| {r_type:<25} | " + " | ".join(w_times) + " |")
        memory_usage_rows.append(f"| {r_type:<25} | " + " | ".join(m_usages) + " |")

    return '\n'.join(wall_time_rows), '\n'.join(memory_usage_rows)


# Read input data from standard input
input_lines = []
try:
    while True:
        block_lines = []
        while True:
            line = input()
            if not line.strip():  # Skip empty lines
                break
            block_lines.append(line)
        if block_lines:  # Proceed if there are non-empty lines
            input_lines.append(block_lines)
except EOFError:
    pass

# Process the input and generate the tables
wall_times, memory_usages = defaultdict(list), defaultdict(list)
for block in input_lines:
    block_wall_times, block_memory_usages = parse_input(block)
    for k, v in block_wall_times.items():
        wall_times[k].extend(v)
    for k, v in block_memory_usages.items():
        memory_usages[k].extend(v)
wall_time_table, memory_usage_table = generate_markdown_tables(wall_times, memory_usages)

# Output the tables
print("### Average Run Times (mean) / (median) / (stddev)")
print(wall_time_table)
print("\n### Average Memory Usage (mean) / (median) / (stddev)")
print(memory_usage_table)


import csv
import re
import os

def fix_time_format(time_str):
    """Converts times like '24:05' to '00:05', '25:10' to '01:10', etc."""
    h, m = map(int, time_str.split(":"))
    h = h % 24
    return f"{h:02d}:{m:02d}"

def filter_csv(input_file, output_file, strings_to_remove):
    """
    Reads a CSV file and writes a new version without lines containing specific strings
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
        strings_to_remove (list): List of strings to filter out
    """
    with open(input_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        for row in reader:
            # Convert row to string for comparison
            row_str = ','.join(row)
            
            # Check if none of the strings to remove are in this row
            if not any(remove_str in row_str for remove_str in strings_to_remove):
                writer.writerow(row)

def extract_epanet_data(rpt_file_path, output_csv_path_nodes, output_csv_path_links):
    """
    Extracts data from an EPANET .rpt file and saves it into two CSV files:
    one for nodes and one for links.

    :param rpt_file_path: Path to the EPANET .rpt file.
    :param output_csv_path_nodes: Path to save the nodes data CSV file.
    :param output_csv_path_links: Path to save the links data CSV file.
    """
    with open(rpt_file_path, 'r') as rpt_file:
        lines = rpt_file.readlines()

    # Initialize variables
    node_data = []
    link_data = []
    current_section = None
    time_step = None

    # Regex to match time in "Link Results at 1:00 Hrs:" or "Node Results at 1:00 Hrs:"
    time_pattern = re.compile(r'(Node|Link) Results at ([\d:]+) Hrs')

    # Parse the .rpt file
    for line in lines:
        line = line.strip()

        # Detect the start of a new section and extract time
        match = time_pattern.match(line)
        if match:
            current_section = "nodes" if match.group(1) == "Node" else "links"
            time_step = fix_time_format(match.group(2))
            continue
        elif line == "":
            current_section = None  # End of a section

        # Parse node data
        if current_section == "nodes" and line:
            parts = line.split()
            if len(parts) >= 4:
                node_id = parts[0]
                demand = parts[1]
                head = parts[2]
                pressure = parts[3]
                node_data.append([time_step, node_id, demand, head, pressure])

        # Parse link data
        elif current_section == "links" and line:
            parts = line.split()
            if len(parts) >= 5:
                link_id = parts[0]
                flow = parts[1]
                velocity = parts[2]
                head_loss = parts[3]
                status = parts[4]
                link_data.append([time_step, link_id, flow, velocity, head_loss, status])

    # Write node data to CSV (overwrite file, so header only once)
    with open(output_csv_path_nodes, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Time", "Node_ID", "Demand (LPS)", "Head (m)", "Pressure (m)"])
        writer.writerows(node_data)

    # Write link data to CSV (overwrite file, so header only once)
    with open(output_csv_path_links, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Time", "Link_ID", "Flow (LPS)", "Velocity (m/s)", "Head_Loss (m)", "Status"])
        writer.writerows(link_data)


# File paths
rpt_file_path = "L-TOWN_Real_out.rpt"  # Update this path if the file is in a different location
output_csv_path_nodes = "epanet_results_nodes.csv"
output_csv_path_links = "epanet_results_links.csv"

# Run the extraction
extract_epanet_data(rpt_file_path, output_csv_path_nodes, output_csv_path_links)

#filter the output
input_csv = 'epanet_results_nodes.csv'
output_csv = 'epanet_results_nodes_filtered.csv'
strings_to_filter = ["Node,Demand,Head,Pressure", "ID,CMH,m,m", "Link,Flow,VelocityUnit,Headloss,Status"]
filter_csv(input_csv, output_csv, strings_to_filter)


input_csv = 'epanet_results_links.csv'
output_csv = 'epanet_results_links_filtered.csv'
strings_to_filter = ["Node,Demand,Head,Pressure", "ID,CMH,m,m", "Link,Flow,VelocityUnit,Headloss,Status"]
filter_csv(input_csv, output_csv, strings_to_filter)

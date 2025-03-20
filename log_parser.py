import re
import sys
import csv
import os
import time
from datetime import datetime, timedelta

def check_for_old_log_line(line):
    if re.search(
            r'Checking if we should notify about stashing (.*?) (\{.*?\})',
            line
        ) is not None:
            print("Found old log file line. Please check if you changed the code in the stash.go file in your bot. Refer to README file.")
            # Cross-platform "Press any key to continue"
            if os.name == 'nt':  # Windows
                os.system('pause')
            else:  # Unix-based systems
                input("Press Enter to exit...")
            sys.exit(1)

def extract_character_name(logfile_name):
    """
    Extracts the character name from the logfile name.
    Example: "Supervisor-log-SCL Horker (dj_hollow)-2025-03-01-12-55-14.txt" -> "SCL Horker (dj_hollow)"
    """
    match = re.search(r'Supervisor-log-(.*?)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.txt', logfile_name)
    if match:
        return match.group(1).strip()
    return "Unknown"

def build_entry(debug_match, info_match, logfile_path, timestamp):
    item_name = info_match.group(2).strip()  # Extract item name
    item_type = info_match.group(3).strip()  # Extract item type
    nip_file = info_match.group(4).strip()  # Extract .nip file path
    line_number = info_match.group(5).strip()  # Extract line number
    raw_rule = info_match.group(6).strip()  # Extract raw rule
    
    # Extract additional attributes from the debug line
    ethereal = debug_match.group(2).strip()
    quality = debug_match.group(3).strip()
    level_req = debug_match.group(4).strip()
    base_stats = debug_match.group(5).strip()
    stats = debug_match.group(6).strip()
    has_sockets = debug_match.group(7).strip()
    sockets = debug_match.group(8).strip()
    unique_set_id = debug_match.group(9).strip()
    desc_type = debug_match.group(10).strip()  # Extract item type from Desc().Type
    
    # Use the item type from Desc().Type for runes and other items
    if desc_type == "rune":
        quality = "Rune"

    # Extract logfile_name from logfile_path
    logfile_name = os.path.basename(logfile_path)

    # Extract character name from the logfile name
    character_name = extract_character_name(logfile_name)

    if "gem" in desc_type:
        return "gem"
    
    # Create a unique identifier for the entry
    return (
        timestamp, character_name, item_name, ethereal, quality, level_req,
        base_stats, stats, has_sockets, sockets, unique_set_id, nip_file, line_number, raw_rule, logfile_name
    )

def write_entries_to_output(output_file, stashed_items):
    # Check if the output file already exists
    file_exists = os.path.isfile(output_file)
    
    with open(output_file, 'a', encoding='utf-8', newline='') as out_file:
        writer = csv.writer(out_file)
        if not file_exists:
            # Write header if the file is new
            writer.writerow([
                "Timestamp", "Character", "Item Name", "Ethereal", "Quality", "Level Req",
                "Base Stats", "Stats", "Has Sockets", "Sockets", "Unique/Set ID", "Nip File", "Line Number", "Raw Rule", "Logfile"
            ])
        writer.writerows(stashed_items)

def extract_stashed_items(logfile_path, output_file, existing_entries):
    stashed_items = []
    previous_line = ""
    entries_added = 0  # Track if any entries were added from this logfile
    valid_entries_found = 0  # Track if the logfile contains valid entries
    
    try:
        # Check if the log file exists
        if not os.path.isfile(logfile_path):
            print(f"Error: The file {logfile_path} does not exist.", flush=True)
            return
        
        with open(logfile_path, 'r', encoding='utf-8') as file:
            previous_date = datetime.fromtimestamp(os.path.getctime(logfile_path)).date()
            for line in file:
                if line.strip() == "":
                    continue
                check_for_old_log_line(line)

                debug_match = re.search(
                    r'Checking if we should notify about stashing (.*?) (true|false) (\w+) (\d+) (\[.*?\]) (\[.*?\]) (true|false) (\[\]|\d+) (\[\]|\d+) (\w+)',
                    previous_line
                )
                info_match = re.search(
                    r'time=(\d{2}:\d{2}:\d{2}).*?msg="Item (.*?) \[(.*?)\] stashed".*?nipFile="?(.*?):(\d+).*?rawRule="(.*?)"',
                    line
                )
                
                #if debug_match:
                #    print(f"Debug match found: {debug_match.groups()}", flush=True)
                #if info_match:
                #    print(f"Info match found: {info_match.groups()}", flush=True)
                log_time_str = re.search(r'time=(\d{2}:\d{2}:\d{2})', line).group(1).strip()
                log_time = datetime.strptime(log_time_str, "%H:%M:%S").time()
                    
                # Check if the time goes from 23:59 to 00:00
                if log_time and previous_line:
                    previous_log_time_str = re.search(r'time=(\d{2}:\d{2}:\d{2})', previous_line).group(1).strip()
                    previous_log_time = datetime.strptime(previous_log_time_str, "%H:%M:%S").time()
                    if previous_log_time > log_time:
                        previous_date += timedelta(days=1)
                    
                timestamp = datetime.combine(previous_date, log_time).strftime("%Y-%m-%d %H:%M:%S")       

                if debug_match and info_match:
                    valid_entries_found += 1
                       
                    entry = build_entry(debug_match, info_match, logfile_path, timestamp)
                    
                    # Skip item type gem
                    if entry == "gem":
                        continue
                    
                    # Check if the entry already exists to avoid duplicates
                    if entry not in existing_entries:
                        stashed_items.append(entry)
                        existing_entries.add(entry)  # Add to the set of existing entries
                        entries_added += 1
                
                previous_line = line  # Update previous_line
        
        write_entries_to_output(output_file, stashed_items)
        
        if entries_added > 0:
            print(f"{entries_added} entries from {logfile_path} have been added to {output_file}.", flush=True)
        elif valid_entries_found > 0:
            print(f"No new entries added from {logfile_path} (all entries are duplicates).", flush=True)
        else:
            print(f"No valid entries found in {logfile_path}.", flush=True)
    except Exception as e:
        print(f"Error occurred while processing {logfile_path}: {e}", flush=True)

def process_folder(folder_path, output_file, existing_entries):
    """
    Processes all log files in a folder.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid folder.", flush=True)
        return
    
    print(f"Processing folder: {folder_path}", flush=True)
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt"):
                logfile_path = os.path.join(root, file)
                extract_stashed_items(logfile_path, output_file, existing_entries)

def load_existing_entries(output_file_path, existing_entries):
    # Load existing entries from the output file (if it exists)
    if os.path.isfile(output_file_path):
        print(f"Loading existing entries from {output_file_path}...", flush=True)
        with open(output_file_path, 'r', encoding='utf-8') as out_file:
            reader = csv.reader(out_file)
            next(reader, None)  # Skip header
            for row in reader:
                existing_entries.add(tuple(row))  # Add each row as a tuple to the set
    
    return existing_entries
    

def get_output_file_path():
    # Get the directory where the executable is located
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    
    # Set the output file path to be in the same directory as the executable
    return os.path.join(exe_dir, "MyStashedItems.csv")

def process_input_files(output_file_path, existing_entries):
    # Process each argument (file or folder)
    for path in sys.argv[1:]:
        if os.path.isfile(path):
            extract_stashed_items(path, output_file_path, existing_entries)
        elif os.path.isdir(path):
            process_folder(path, output_file_path, existing_entries)
        else:
            print(f"Error: {path} is neither a file nor a folder.", flush=True)

def close_terminal_after_delay(seconds):
    # Display the message
    print(f"The terminal will close in {seconds} seconds...")
    
    # Wait for the specified number of seconds
    time.sleep(seconds)
    
    # Close the terminal
    if os.name == 'nt':  # Windows
        os.system('exit')
    else:  # Unix-based systems
        os.system('kill -9 $PPID')  # Kill the parent process

def main():
    if len(sys.argv) < 2:
        print("Please drag and drop one or more logfiles or a folder onto the script or provide them as arguments.", flush=True)
    else:
        output_file_path = get_output_file_path()

        existing_entries = load_existing_entries(output_file_path, set())
        
        process_input_files(output_file_path, existing_entries)

if __name__ == "__main__":
    main()

    close_terminal_after_delay(15)
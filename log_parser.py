import re
import sys
import csv
import os
from datetime import datetime

def extract_character_name(logfile_name):
    """
    Extracts the character name from the logfile name.
    Example: "Supervisor-log-SCL Horker (dj_hollow)-2025-03-01-12-55-14.txt" -> "SCL Horker (dj_hollow)"
    """
    match = re.search(r'Supervisor-log-(.*?)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.txt', logfile_name)
    if match:
        return match.group(1).strip()
    return "Unknown"

def extract_stashed_items(logfile_path, output_file, existing_entries):
    stashed_items = []
    previous_line = ""
    logfile_name = os.path.basename(logfile_path)
    entries_added = 0  # Track if any entries were added from this logfile
    valid_entries_found = 0  # Track if the logfile contains valid entries
    
    try:
        # Check if the log file exists
        if not os.path.isfile(logfile_path):
            print(f"Error: The file {logfile_path} does not exist.", flush=True)
            return
        
        # Get the last modified date of the logfile
        logfile_date = datetime.fromtimestamp(os.path.getmtime(logfile_path)).strftime("%Y-%m-%d")
        
        # Extract character name from the logfile name
        character_name = extract_character_name(logfile_name)
        
        with open(logfile_path, 'r', encoding='utf-8') as file:
            for line in file:
                if re.search(
                    r'Checking if we should notify about stashing (.*?) (\{.*?\})',
                    line
                ) is not None:
                    print(f"Found old log file line. Please check if you changed the code in the stash.go file in your bot. Refer to README file.")
                    # Cross-platform "Press any key to continue"
                    if os.name == 'nt':  # Windows
                        os.system('pause')
                    else:  # Unix-based systems
                        input("Press Enter to exit...")
                    sys.exit(1)

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
                
                if debug_match and info_match:
                    valid_entries_found += 1  # Logfile contains valid entries
                    log_time = info_match.group(1).strip()  # Extract log timestamp
                    item_name = info_match.group(2).strip()  # Extract item name
                    item_type = info_match.group(3).strip()  # Extract item type
                    nip_file = info_match.group(4).strip()  # Extract .nip file path
                    line_number = info_match.group(5).strip()  # Extract line number
                    raw_rule = info_match.group(6).strip()  # Extract raw rule
                    
                    # Extract additional attributes from the debug line
                    ethereal = debug_match.group(2).strip() == "true"
                    quality = debug_match.group(3).strip()
                    level_req = int(debug_match.group(4).strip())
                    base_stats = debug_match.group(5).strip()
                    stats = debug_match.group(6).strip()
                    has_sockets = debug_match.group(7).strip() == "true"
                    sockets = debug_match.group(8).strip()
                    unique_set_id = debug_match.group(9).strip()
                    desc_type = debug_match.group(10).strip()  # Extract item type from Desc().Type
                    
                    # Use the item type from Desc().Type for runes and other items
                    if desc_type == "rune":
                        quality = "Rune"

                    # Skip item type gem
                    if "gem" in desc_type: 
                        continue
                    
                    # Combine logfile date and log timestamp
                    timestamp = f"{logfile_date} {log_time}"
                    
                    # Create a unique identifier for the entry
                    entry = (
                        timestamp, character_name, item_name, ethereal, quality, level_req,
                        base_stats, stats, has_sockets, sockets, unique_set_id, nip_file, line_number, raw_rule, logfile_name
                    )
                    
                    # Check if the entry already exists to avoid duplicates
                    if entry not in existing_entries:
                        stashed_items.append(entry)
                        existing_entries.add(entry)  # Add to the set of existing entries
                        entries_added += 1
                
                previous_line = line  # Update previous_line
        
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
        
        if entries_added > 0:
            print(f"Data from {logfile_path} has been added to {output_file}.", flush=True)
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

def main():
    # Get the directory where the executable is located
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    
    # Set the output file path to be in the same directory as the executable
    output_file = os.path.join(exe_dir, "MyStashedItems.csv")
    
    if len(sys.argv) < 2:
        print("Please drag and drop one or more logfiles or a folder onto the script or provide them as arguments.", flush=True)
    else:
        existing_entries = set()  # Track existing entries to avoid duplicates
        
        # Load existing entries from the output file (if it exists)
        if os.path.isfile(output_file):
            print(f"Loading existing entries from {output_file}...", flush=True)
            with open(output_file, 'r', encoding='utf-8') as out_file:
                reader = csv.reader(out_file)
                next(reader, None)  # Skip header
                for row in reader:
                    existing_entries.add(tuple(row))  # Add each row as a tuple to the set
        
        # Process each argument (file or folder)
        for path in sys.argv[1:]:
            if os.path.isfile(path):
                extract_stashed_items(path, output_file, existing_entries)
            elif os.path.isdir(path):
                process_folder(path, output_file, existing_entries)
            else:
                print(f"Error: {path} is neither a file nor a folder.", flush=True)
        
        # Wait for user input (cross-platform)
        if sys.stdin is not None and sys.stdin.isatty():
            input("Press Enter to exit...")  # Wait for input only in the console
        else:
            # Cross-platform "Press any key to continue"
            if os.name == 'nt':  # Windows
                os.system('pause')
            else:  # Unix-based systems
                input("Press Enter to exit...")

if __name__ == "__main__":
    main()
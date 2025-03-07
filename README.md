Koolo Log Parser and Stash Tracker

This Python script parses Koolo character log files and extracts information about stashed items. It generates a CSV file (MyStashedItems.csv) containing detailed item information, including name, type, quality, stats, and more. This tool is particularly useful for tracking collected items and analyzing your stash in Diablo 2.

🚀 Features

✅ Log File Parsing – Extracts item details from Diablo 2 log files.✅ CSV Output – Generates a CSV file with the following columns:

Timestamp

Character Name

Item Name

Ethereal Status

Quality (Normal, Magic, Rare, Unique, Rune)

Level Requirement

Base Stats

Additional Stats

Socket Information

Unique/Set ID

NIP File Path

Line Number in NIP File

Raw Rule

Logfile Name✅ Duplicate Prevention – Prevents duplicate entries in the CSV file.✅ Folder Support – Process multiple log files by dragging and dropping a folder onto the script.✅ Cross-Platform – Works on Windows, macOS, and Linux.

📌 How It Works

The script reads Diablo 2 log files, scans for debug and info messages related to stashed items, extracts relevant data, and writes it to a CSV file. Duplicate entries are handled, ensuring clean data in the output.

🛠 Usage

Prerequisites

Python 3.x installed

No additional dependencies (uses built-in libraries)

🔧 Running the Script

Clone the Repository:

git clone https://github.com/your-username/diablo2-log-parser.git
cd diablo2-log-parser

Run the Script:
Drag and drop a log file or folder onto the script (if compiled as an executable), or run from the command line:

python script.py path/to/logfile.txt

Or for a folder:

python script.py path/to/folder

Output:

Generates a CSV file named MyStashedItems.csv in the script directory.

Contains extracted item information.

📦 Compiling to an Executable

To create an executable for easier use:

Install pyinstaller:

pip install pyinstaller

Compile the script:

pyinstaller --onefile --console script.py

The executable will be located in the dist folder.

📜 Example Log Entry

time=21:03:45 level=DEBUG msg="Checking if we should notify about stashing GrandCharm false 4 42 [] [40% Extra Gold from Monsters +1 to Fire Skills (Sorceress only) Required Level: 42] false [] 0 lcha"
time=21:03:45 level=INFO msg="Item Grand Charm [Magic] stashed" nipFile="C:\path\to\pickit\magic.nip:2" rawRule="[name] == grandcharm && [quality] == magic # [fireskilltab] >= 1"

📊 Example CSV Output

Timestamp

Character

Item Name

Ethereal

Quality

Level Req

Stats

Has Sockets

Unique/Set ID

NIP File

Raw Rule

2025-03-01 12:55:14

Frosti-tute

Grand Charm

false

Magic

42

40% Extra Gold...

false

0

C:\path\to\pickit\magic.nip

[name] == grandcharm && [quality] == magic # [fireskilltab] >= 1

🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request with suggestions, bug reports, or feature requests.

📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

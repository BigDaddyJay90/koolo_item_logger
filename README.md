<ins>**#INFO: Right now, this only works with an edited version of koolo/internal/action/stash.go**<ins>


Original Lines:
```
ctx.Logger.Debug(fmt.Sprintf("Checking if we should notify about stashing %s %v", i.Name, i.Desc()))
	// Don't notify about gems
	if strings.Contains(i.Desc().Type, "gem") {
		return false
	}

````

Updated Lines needed for the Logging Tool:

```
ctx.Logger.Debug(fmt.Sprintf("Checking if we should notify about stashing %v %t %v %v %v %v %v %v %v %v", i.Name, i.Ethereal, i.Quality.ToString(), i.LevelReq, i.BaseStats, i.Stats, i.HasSockets, i.Sockets, i.UniqueSetID, i.Desc().Type))
    // Don't notify about gems
    if strings.Contains(i.Desc().Type, "gem") {
        return false
    }
```

# Logfile Parser and Stashed Items Extractor

This Python script parses Koolo logfiles to extract stashed item details. It processes logfiles, avoids duplicates, and saves data to a CSV file.

## Features
- **Logfile Parsing**: Extracts character names and item details.
- **Duplicate Prevention**: Skips existing entries in the CSV.
- **CSV Export**: Saves data to `MyStashedItems.csv`.
- **Batch Processing**: Handles single files or entire folders.

## Requirements for building from source
- Python 3.x
- Packages: `re`, `csv`, `os`, `datetime` (included in Python’s standard library).

## Usage

### 1. Process a Single Logfile
Drag-and-drop the logfile onto the script or run:  
`python log_parser.py "path/to/logfile.txt"`

### 2. Process a Folder of Logfiles
Drag-and-drop the Folder onto the script or run:  
`python log_parser.py "path/to/logfiles_folder"`

### 3. Output File (`MyStashedItems.csv`)
The CSV includes these columns:
- **Timestamp**: Date/time of the stash action.
- **Character**: Character name (extracted from the logfile name).
- **Item Name**: Name of the stashed item.
- **Ethereal**: `true`/`false` if the item is ethereal.
- **Quality**: Item quality (e.g., Rune, Magic).
- **Level Req**: Required level to use the item.
- **Base Stats**: Base stats of the item (JSON array).
- **Stats**: Additional stats (JSON array).
- **Has Sockets**: `true`/`false` if the item has sockets.
- **Sockets**: Number of sockets (e.g., `[3]`).
- **Unique/Set ID**: ID for unique/set items.
- **Nip File**: Path to the `.nip` rule file.
- **Line Number**: Line number in the `.nip` file.
- **Raw Rule**: The rule that triggered the stash.
- **Logfile**: Source logfile name.

## How It Works
1. **Extract Character Name**: Uses regex to parse the logfile name.
2. **Parse Log Entries**: Matches debug and info lines to extract item details.
3. **Avoid Duplicates**: Checks against existing CSV entries.
4. **Save to CSV**: Appends new entries to `MyStashedItems.csv`.

## Example Logfile Format
Logfiles are expected to have names like:  
`Supervisor-log-charactername-year-month-day-hh-mm-ss.txt`

## Notes
- Errors (e.g., missing files) are logged to the console.
- The script will auto exit terminal after a fixed time.

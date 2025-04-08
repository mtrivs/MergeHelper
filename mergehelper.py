#!/usr/bin/env python3
"""
'MergeHelper v1.1' by mtrivs

This script facilitates batch conversion of multi-track disc images into a single BIN/CUE pair using the binmerge tool.
It searches for folders containing more than one BIN file and merges them based on the data from the CUE sheet.
The script will skip folders where no CUE files are present or if multiple CUE files are found in the same directory.
If a merge operation fails, the script cleans up by restoring the original files.

Copyright (C) 2024 Mitch Trivison (https://github.com/mtrivs)
binmerge python script created by Chris Putnam (https://github.com/putnam/binmerge)

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

Please report any bugs on GitHub: https://github.com/mtrivs/MergeHelper
"""

import os, sys, shutil, time, logging, urllib.request, subprocess

##############################################################################################
# START USER CONFIGURABLE VARIABLES
##############################################################################################
GAMEROOT = r"/mnt/c/Users/mtriv/OneDrive/Documents/Scripts/MergeHelper/roms/roms"
"""
Root directory containing game folders with BIN/CUE files to be merged.
"""

NAMEBY = "folder"
"""
Determines how the merged BIN/CUE files are named: by folder name or CUE file name.
"""

REMOVEMODE = "2"
"""
Determines whether original files are deleted after a successful merge.
Options:
    "0" - no removal
    "1" - remove if successful
    "2" - prompt user
"""

ENABLE_LOGGING = True
"""
Enables or disables logging to a file.
"""

VERBOSE_LOGGING = False
"""
Enables or disables detailed logging for debugging purposes.
"""

##############################################################################################
# END USER CONFIGURABLE VARIABLES
##############################################################################################

class Game:
    """
    Represents a game directory containing BIN/CUE files to be merged.

    Attributes:
        name (str): The name of the game, derived from the folder or CUE file.
        directory (str): The path to the game directory.
        cue_file (str): The path to the CUE file in the directory.
        bin_count (int): The number of BIN files present in the directory.

    Methods:
        __repr__(): Returns a string representation of the Game object for debugging purposes.
    """
    def __init__(self, name, directory, cue_file, bin_count):
        self.name = name  # Name of the game (folder or CUE-based)
        self.directory = directory  # Path to the game directory
        self.cue_file = cue_file  # Path to the CUE file
        self.bin_count = bin_count  # Number of BIN files in the directory

    def __repr__(self):
        return f"Game(name={self.name}, directory={self.directory}, cue_file={self.cue_file}, bin_count={self.bin_count})"

# Refactor to eliminate redundancy by reusing PaddedFormatter for both console and file handlers
class PaddedFormatter(logging.Formatter):
    """
    A logging formatter that ensures consistent padding for log levels.

    Attributes:
        log_fixed_width (int): The fixed width for log level names to ensure alignment.
    """
    def format(self, record):
        log_fixed_width = 8  # Fixed width for log levels
        record.levelname = f"{record.levelname:<{log_fixed_width}}"  # Pad the log level
        return super().format(record)

class ColorizedFormatter(PaddedFormatter):
    """
    A logging formatter that applies colorization to log levels and messages for console output.

    Inherits:
        PaddedFormatter: Ensures consistent padding for log levels.

    Methods:
        format(record): Formats the log record with color codes for log levels and messages.
    """
    def format(self, record):
        # Get the color for the log level
        log_color = COLORS.get(record.levelname.strip(), COLORS["RESET"])

        # Apply color to the log level and message, ensuring padding is applied after colorization
        padded_levelname = f"{record.levelname.strip():<{8}}"  # Apply padding to the stripped level name
        record.levelname = f"{log_color}{padded_levelname}{COLORS['RESET']}"
        record.msg = f"{log_color}{record.msg}{COLORS['RESET']}"

        return super().format(record)

# Path and URL for binmerge script
BINMERGE_URL = "https://raw.githubusercontent.com/putnam/binmerge/master/binmerge"
BINMERGE_PATH = "./BinMerge.py"

# Configure logging for console (colorized) and file (plain text)
LOG_FILE = "mergehelper.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%m-%d-%Y %H:%M:%S"  # Updated to exclude milliseconds

# ANSI color codes for log levels
COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",   # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",   # Red
    "CRITICAL": "\033[41m",  # Red background
    "RESET": "\033[0m"    # Reset to default
}

# Determine the logging level based on VERBOSE_LOGGING
LOG_LEVEL = logging.DEBUG if VERBOSE_LOGGING is True else logging.INFO

# Create logger for console output (colorized) with consistent naming
console_logger = logging.getLogger("console_logger")
console_logger.setLevel(LOG_LEVEL)

# Create stream handler with colorized output for console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(LOG_LEVEL)
stream_handler.setFormatter(ColorizedFormatter("[%(levelname)s] %(message)s"))  # Colorized for console
console_logger.addHandler(stream_handler)

# Create logger for file output (plain text) only if logging is enabled
if ENABLE_LOGGING:
    file_logger = logging.getLogger("FileLogger")
    file_logger.setLevel(logging.DEBUG)

    # Create file handler with plain text output for log file
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(LOG_LEVEL)

    # Update the file handler to use the PaddedFormatter
    file_handler.setFormatter(PaddedFormatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    file_logger.addHandler(file_handler)

# Logging helper functions for different log levels.
def info(message, *args):
    """
    Log an info message.
    """
    console_logger.info(message, *args)
    if ENABLE_LOGGING:
        file_logger.info(message, *args)

def detail(message, *args):
    """
    Log a debug message (used for verbose logging).
    """
    if VERBOSE_LOGGING:
        console_logger.debug(message, *args)
    if ENABLE_LOGGING:
        file_logger.debug(message, *args)

def warn(message, *args):
    """
    Log a warning message.
    """
    console_logger.warning(message, *args)
    if ENABLE_LOGGING:
        file_logger.warning(message, *args)

def fail(message, *args):
    """
    Log an error message.
    """
    console_logger.error(message, *args)
    if ENABLE_LOGGING:
        file_logger.error(message, *args)

# Function to check dependencies required by the script.
def check_dependencies():
    """
    Ensure all required dependencies are available.
    """
    info("*** BEGIN dependency pre-check ***")
    
    # Check Python version.
    if sys.version_info[0] < 3:
        fail("   [-] This script requires Python 3 or later.")
        sys.exit(1)
    info("   [+] Python version check passed")

    # Ensure binmerge script is available.
    if not os.path.exists(BINMERGE_PATH):
        info(f"   [-] BinMerge script not found. Downloading from {BINMERGE_URL}...")
        try:
            urllib.request.urlretrieve(BINMERGE_URL, BINMERGE_PATH)
            info("   [+] BinMerge script downloaded successfully.")
        except Exception as e:
            fail(f"   [-] Failed to download BinMerge script: {e}")
            sys.exit(1)
    else:
        info("   [+] BinMerge script is available.")

    info("*** FINISH Dependency pre-check ***")

def display_progress(current, total, bar_length=50):
    """
    Display a progress bar in the console.

    Parameters:
        current (int): The current progress count.
        total (int): The total count for completion.
        bar_length (int): The length of the progress bar (default is 50).
    """
    progress = current / total
    block = int(bar_length * progress)
    bar = "█" * block + "-" * (bar_length - block)
    info(f"Progress: |{bar}| {current}/{total} ({progress * 100:.2f}%)")

def merge_bin_files(orig_dir, GAMEDIR, GAMENAME, REMOVEMODE):
    """
    Merge BIN/CUE files using the binmerge script.
    """
    info("    ├── Merging BIN files with binmerge")
    try:
        # Find the CUE file in the backup directory
        new_cue = [file for file in os.listdir(orig_dir) if file.lower().endswith(".cue")][0]
        cue_file_path = os.path.join(orig_dir, new_cue)  # Construct the full path to the CUE file

        # Log the output filename for clarity
        detail("    ├── Merging files with output name: %s", GAMENAME)

        # Adjust command based on VERBOSE_LOGGING
        if VERBOSE_LOGGING:
            command = ["python3", "-u", BINMERGE_PATH, cue_file_path, GAMENAME, "-o", GAMEDIR, "-v"]
        else:
            command = ["python3", "-u", BINMERGE_PATH, cue_file_path, GAMENAME, "-o", GAMEDIR]

        detail("    ├── Executing command:")
        detail("    ├──── %s", " ".join(command))

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, env={**os.environ, "PYTHONUNBUFFERED": "1"})

        # Capture and log stdout and stderr in real-time
        for line in process.stdout:
            # Strip any leading/trailing whitespace and the existing lognames from binmerge
            stripped_line = line[7:].strip() 
            if VERBOSE_LOGGING:
                detail("    ├────── %s", stripped_line)
            else:
                info("    ├────── %s", stripped_line)
            sys.stdout.flush()  # Ensure real-time rendering

        for line in process.stderr:
            # Strip any leading/trailing whitespace and the existing lognames from binmerge
            stripped_line = line[7:].strip() 
            fail("    ├────── %s", stripped_line)
            sys.stderr.flush()  # Ensure real-time rendering

        process.wait()
        if process.returncode != 0:
            raise Exception(f"BinMerge failed with return code {process.returncode}")
        else:
            info("    ├── BinMerge completed successfully.")

        # Handle file removal based on REMOVEMODE
        if REMOVEMODE == "1":
            try:
                shutil.rmtree(orig_dir)
                info("    ├── Original multi-track bin files removed!")
            except Exception as e:
                fail("    ├── Failed to remove original multi-track files: %s", e)
                fail("    └── Original multi-track files can be found in backup directory")
        else:
            info("    ├── Original multi-track files can be found in backup directory")

        info("    └── Successfully completed processing of %s", GAMENAME)

    except Exception as e:
        fail("    └── Merge failed! Error: %s", e)
        fail("    └── Removing any partial BIN/CUE files and moving original files back!")

        # Cleanup partial files in GAMEDIR
        for file in os.listdir(GAMEDIR):
            if file.lower().endswith(('.cue', '.bin')):
                os.remove(os.path.join(GAMEDIR, file))

        # Restore original files from orig_dir
        for file in os.listdir(orig_dir):
            try:
                shutil.move(os.path.join(orig_dir, file), GAMEDIR)
            except Exception as exc:
                fail("    └── Failed to move file %s back to %s. Error: %s", file, GAMEDIR, exc)

        # Remove the orig_dir if empty
        try:
            os.rmdir(orig_dir)
        except OSError:
            fail("    └── Could not remove backup directory %s. It may not be empty.", orig_dir)

def scan_directories(GAMEROOT, NAMEBY):
    """
    Scan all sub-directories in GAMEROOT and build a list of games to be merged.

    Parameters:
        GAMEROOT (str): The root directory containing game folders with BIN/CUE files.
        NAMEBY (str): Determines how the merged BIN/CUE files are named. Options:
                      - "folder": Use the folder name.
                      - "cue": Use the CUE file name.

    Returns:
        list[Game]: A list of Game objects representing directories to be merged.
    """
    info("*** BEGIN scanning directories ***")
    games_to_merge = []
    game_dirs = [entry for entry in os.scandir(GAMEROOT) if entry.is_dir()]
    for GAMEDIR in game_dirs:
        GAMEDIR = os.path.join(GAMEROOT, GAMEDIR)
        if os.path.isdir(GAMEDIR):
            files_in_dir = os.listdir(GAMEDIR)
            BINCOUNT = len([file for file in files_in_dir if file.lower().endswith(".bin")])
            CUECOUNT = len([file for file in files_in_dir if file.lower().endswith(".cue")])
            if CUECOUNT == 1:
                cue_files = [file for file in os.listdir(GAMEDIR) if file.lower().endswith(".cue")]
                cue_file_path = os.path.join(GAMEDIR, cue_files[0])
                if NAMEBY == "cue":
                    GAMENAME = os.path.splitext(cue_files[0])[0]  # Use CUE file name without extension
                else:
                    GAMENAME = os.path.basename(GAMEDIR)  # Use folder name
            elif CUECOUNT > 1:
                fail("    └── Multiple CUE files found in %s. Skipping merge.", GAMEDIR)
                fail("    └── CUE files found: %s", [file for file in files_in_dir if file.lower().endswith(".cue")])
                continue
            else:
                fail("    └── No CUE file found in %s. Skipping merge.", GAMEDIR)
                continue

            if BINCOUNT > 1:
                info("    ├── Game %s identified for merging.", GAMENAME)
                games_to_merge.append(Game(GAMENAME, GAMEDIR, cue_file_path, BINCOUNT))
            elif BINCOUNT == 1:
                detail("    ├── No merge needed for %s", GAMENAME)
            else:
                fail("    └── No BIN files found for %s", GAMENAME)

    info("*** FINISHED scanning directories ***")
    return games_to_merge

# Update the process_games function to include the progress indicator
def process_games(games, REMOVEMODE):
    """
    Process a list of games and merge their BIN/CUE files.

    Parameters:
        games (list[Game]): A list of Game objects to process.
        REMOVEMODE (str): Specifies the behavior for handling original files after a successful merge.

    Returns:
        None
    """
    info("*** BEGIN merging games ***")
    total_games = len(games)
    display_progress(0, total_games)  # diaplay initial progress bar
    for index, game in enumerate(games, start=1):
        info("Now processing %s", game.name)
        orig_dir = os.path.join(game.directory, 'orig')
        if os.path.exists(orig_dir) and os.listdir(orig_dir):
            fail("    └── Backup directory already exists and contains files. Skipping %s to avoid overwriting.", game.directory)
            display_progress(index, total_games)  # Update progress bar
            continue
        os.makedirs(orig_dir, exist_ok=True)
        try:
            cue_bin_files = [file for file in os.listdir(game.directory) if file.lower().endswith(('.cue', '.bin'))]
            for file in cue_bin_files:
                shutil.move(os.path.join(game.directory, file), orig_dir)
                detail("    ├── Moved file %s to backup directory %s", file, orig_dir)
            info("    ├── All original files moved to backup directory %s", orig_dir)
            merge_bin_files(orig_dir, game.directory, game.name, REMOVEMODE)
        except Exception as exc:
            fail("    └── Failed to process game %s. Error: %s", game.name, exc)
            continue
        finally:
            display_progress(index, total_games)  # Update progress bar
    info("*** FINISHED merging games ***")

"""
Main function to execute the script logic.
"""
try:
    check_dependencies()
except Exception as e:
    fail("Critical error: %s", e)
    sys.exit(1)

info(" ")
start_time = time.time()
detail("Script started at: %s", time.strftime('%m-%d-%Y %H:%M:%S'))
print("""\033[32m
    ███╗░░░███╗███████╗██████╗░░██████╗░███████╗██╗░░██╗███████╗██╗░░░░░██████╗░███████╗██████╗░
    ████╗░████║██╔════╝██╔══██╗██╔════╝░██╔════╝██║░░██║██╔════╝██║░░░░░██╔══██╗██╔════╝██╔══██╗
    ██╔████╔██║█████╗░░██████╔╝██║░░██╗░█████╗░░███████║█████╗░░██║░░░░░██████╔╝█████╗░░██████╔╝
    ██║╚██╔╝██║██╔══╝░░██╔══██╗██║░░╚██╗██╔══╝░░██╔══██║██╔══╝░░██║░░░░░██╔═══╝░██╔══╝░░██╔══██╗   █░█ ▄█
    ██║░╚═╝░██║███████╗██║░░██║╚██████╔╝███████╗██║░░██║███████╗███████╗██║░░░░░███████╗██║░░██║   ▀▄▀ ░█
    ╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚═╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚══════╝╚══════╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝

                                https://github.com/mtrivs/MergeHelper
                                        Powered by BinMerge!
\033[0m""")

if REMOVEMODE == "2":
    warn(
        "The REMOVEMODE variable has not been configured. This determines whether the original files are deleted after a successful merge operation. Edit the REMOVEMODE variable inside the script to disable this prompt.\n"
        "Your options to proceed are:\n"
        "\tN     KEEP the original (non-merged) game files in the orig folder after the merge process has completed\n"
        "\tY     DELETE the original (non-merged) game files once the merge process has SUCCESSFULLY completed\n"
        "\tQ     QUIT the script\n"
        "                \033[31m******  PROCEED CAREFULLY! DELETING GAME FILES CANNOT BE UNDONE ******")
    DELETEFILES = input(
        "\033[33mWould you like to delete the original game files if the merge process is successful? [y/n/q]: ").lower()
    if DELETEFILES == 'y':
        REMOVEMODE = "1"
        info("Deleting original multi-track files after successful merge operation")
    elif DELETEFILES == 'n':
        REMOVEMODE = "2"
        info("Original BIN/CUE files will be backed up to a new 'orig' folder prior to merge operations")
    elif DELETEFILES == 'q':
        fail("User aborted script....")
        sys.exit(1)
    else:
        fail("Unknown response.  Run the script again and select a valid option")
        sys.exit(1)

games_to_merge = scan_directories(GAMEROOT, NAMEBY)
process_games(games_to_merge, REMOVEMODE)

end_time = time.time()
runtime_seconds = int(end_time - start_time)
hours, remainder = divmod(runtime_seconds, 3600)
minutes, seconds = divmod(remainder, 60)
info("Script ended. Runtime: %02d:%02d:%02d (hh:mm:ss)", hours, minutes, seconds)
print(" ")

#!/usr/bin/env python3
"""
MergeHelper v1.5

This script facilitates batch conversion of multi-track disc images into a single BIN/CUE pair using the binmerge tool.
It recursively scans all subdirectories under the specified GAMEROOT directory to locate BIN/CUE files for merging.

Features:
- Automatically detects and processes multi-track BIN/CUE files.
- Recursively scans directories, eliminating the need for strict folder structures.
- Handles errors gracefully, ensuring original files are restored in case of failure.
- Provides detailed logging and progress tracking.

Usage:
- Set the GAMEROOT variable to the root directory containing game folders.
- Configure other variables like NAMEBY and REMOVEMODE as needed.
- Run the script to process and merge BIN/CUE files.

Note:
Recursive scanning is permanently enabled, simplifying directory handling.

Author: Mitch Trivison (https://github.com/mtrivs)
License: GNU General Public License v2.0 or later

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
GAMEROOT = r"C:\roms"
"""
Root directory containing game folders with BIN/CUE files to be merged.
The directory will be recursively scanned to locate all BIN/CUE files, including those in nested subdirectories.
"""

REMOVEMODE = "2"
"""
Determines whether original files are deleted after a successful merge.
Options:
    "0" - no removal
    "1" - remove if successful
    "2" - prompt user
"""

PYDIR = "python"
"""
Path to the Python interpreter. Default is "python" for Windows and "python3" for Linux/Mac.
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
        bin_files (list[str]): A list of BIN file paths associated with the game.

    Methods:
        __repr__(): Returns a string representation of the Game object for debugging purposes.
    """
    def __init__(self, name, directory, cue_file, bin_count, bin_files):
        self.name = name  # Name of the game (folder or CUE-based)
        self.directory = directory  # Path to the game directory
        self.cue_file = cue_file  # Path to the CUE file
        self.bin_count = bin_count  # Number of BIN files in the directory
        self.bin_files = bin_files  # List of BIN file paths

    def __repr__(self):
        return (f"Game(name={self.name}, directory={self.directory}, cue_file={self.cue_file}, "
                f"bin_count={self.bin_count}, bin_files={self.bin_files})")

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

def merge_bin_files(game, REMOVEMODE):
    """
    Merge BIN/CUE files using the binmerge script.

    Parameters:
        game (Game): The Game object containing details about the game to merge.
        REMOVEMODE (str): Specifies the behavior for handling original files after a successful merge.
    """
    info("    ├── Merging BIN files with binmerge")
    orig_dir = os.path.join(game.directory, "orig")
    try:
        # Transform game.cue_file to reference the CUE file in the orig directory
        orig_cue_file = os.path.join(orig_dir, os.path.basename(game.cue_file))

        # Log the output filename for clarity
        detail("    ├── Merging files with output name: %s", game.name)

        command = [PYDIR, "-u", BINMERGE_PATH, orig_cue_file, game.name, "-o", game.directory]
        if VERBOSE_LOGGING:
            command.append("-v")
        detail("    ├── Executing command:")
        detail("    ├──── %s", " ".join(command))

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, env={**os.environ, "PYTHONUNBUFFERED": "1"})

        # Capture and log stdout and stderr in real-time
        for line in process.stdout:
            stripped_line = line[7:].strip()
            if VERBOSE_LOGGING:
                detail("    ├────── %s", stripped_line)
            else:
                info("    ├────── %s", stripped_line)
            sys.stdout.flush()

        for line in process.stderr:
            stripped_line = line[7:].strip()
            fail("    ├────── %s", stripped_line)
            sys.stderr.flush()

        process.wait()
        if process.returncode != 0:
            raise Exception(f"BinMerge failed with return code {process.returncode}")
        else:
            info("    ├── BinMerge completed successfully.")

        # Handle file removal based on REMOVEMODE
        if REMOVEMODE == "1":
            try:
                # Remove original multi-track files from the orig directory
                for file in game.bin_files + [os.path.basename(game.cue_file)]:
                    os.remove(os.path.join(orig_dir, file))
                info("    ├── Original multi-track bin files removed!")
                # Remove the orig_dir if empty
                if not os.listdir(orig_dir):
                    os.rmdir(orig_dir)
                    detail("    ├── Removed empty backup directory %s", orig_dir)
            except Exception as e:
                fail("    ├── Failed to remove original multi-track files: %s", e)
                fail("    └── Original multi-track files will need to be manually deleted from backup directory")
        else:
            info("    ├── Original multi-track files can be found in backup directory")

        info("    └── Successfully completed processing of %s", game.name)

    except Exception as e:
        fail("    └── Merge failed! Error: %s", e)
        fail("    └── Removing any partial BIN/CUE files and moving original files back!")

        # Cleanup partial files in game.directory
        output_files = {f"{game.name}.bin", f"{game.name}.cue"}
        for file in output_files:
            file_path = os.path.join(game.directory, file)
            if os.path.exists(file_path):
                os.remove(file_path)

        # Restore original files from orig_dir
        for file in game.bin_files + [os.path.basename(game.cue_file)]:
            try:
                shutil.move(os.path.join(orig_dir, file), game.directory)
            except Exception as exc:
                fail("    └── Failed to move file %s back to %s. Error: %s", file, game.directory, exc)

        # Remove the orig_dir if empty
        if not os.listdir(orig_dir):
            os.rmdir(orig_dir)
            detail("    ├── Removed empty backup directory %s", orig_dir)

def scan_directories(GAMEROOT):
    """
    Scan all sub-directories in GAMEROOT and build a list of games to be merged.

    Parameters:
        GAMEROOT (str): The root directory containing game folders with BIN/CUE files.

    Returns:
        list[Game]: A list of Game objects representing directories to be merged.
    """
    info("*** BEGIN scanning directories ***")
    games_to_merge = []
    info("    ├── Scanning all subdirectories under GAMEROOT.")

    for root, dirs, files in os.walk(GAMEROOT):
        # Filter CUE files in the current directory
        cue_files = [file for file in files if file.lower().endswith(".cue")]
        if not cue_files:
            detail("    ├── No CUE files found in %s. Skipping.", root)
            continue

        for cue_file in cue_files:
            cue_file_path = os.path.join(root, cue_file)
            try:
                # Parse the CUE file to extract referenced BIN files
                with open(cue_file_path, 'r', encoding='utf-8') as f:
                    bin_files = []
                    for line in f:
                        if line.strip().upper().startswith("FILE"):
                            try:
                                bin_name = line.split('"')[1]
                                bin_files.append(bin_name)
                            except IndexError:
                                fail("    └── Malformed FILE entry in CUE file %s: %s", cue_file, line.strip())
                                continue

                # Verify all referenced BIN files exist in the same directory
                missing_bins = [bin_file for bin_file in bin_files if not os.path.exists(os.path.join(root, bin_file))]
                if missing_bins:
                    fail("    └── Missing BIN files referenced in %s: %s", cue_file, missing_bins)
                    continue

                # Derive game name from the CUE file name without extension
                game_name = os.path.splitext(cue_file)[0]

                # Count BIN files in the directory
                bin_count = len(bin_files)

                # Add the game to the list if it has multiple BIN files
                if bin_count > 1:
                    info("    ├── Game %s identified for merging.", game_name)
                    games_to_merge.append(Game(game_name, root, cue_file_path, bin_count, bin_files))
                elif bin_count == 1:
                    detail("    ├── No merge needed for %s", game_name)
                else:
                    fail("    └── No BIN files found for %s", game_name)

            except Exception as e:
                fail("    └── Failed to process CUE file %s. Error: %s", cue_file, e)
    info("*** FINISHED scanning directories ***")
    return games_to_merge

def process_games(games, REMOVEMODE):
    """
    Process a list of games and merge their BIN/CUE files.

    Parameters:
        games (list[Game]): A list of Game objects to process.
        REMOVEMODE (str): Specifies the behavior for handling original files after a successful merge.
    """
    info("*** BEGIN merging games ***")
    total_games = len(games)
    display_progress(0, total_games)  # Display initial progress bar
    for index, game in enumerate(games, start=1):
        info("Now processing %s", game.name)
        orig_dir = os.path.join(game.directory, "orig")
        os.makedirs(orig_dir, exist_ok=True)  # Ensure the orig directory exists
        conflicting_files = [file for file in game.bin_files + [os.path.basename(game.cue_file)] if os.path.exists(os.path.join(orig_dir, file))]
        if conflicting_files:
            fail("    └── Backup directory for %s contains conflicting files: %s. Skipping to avoid overwriting.", game.name, conflicting_files)
            display_progress(index, total_games)  # Update progress bar
            continue
        try:
            for file in game.bin_files + [os.path.basename(game.cue_file)]:
                shutil.move(os.path.join(game.directory, file), orig_dir)
                detail("    ├── Moved file %s to backup directory %s", file, orig_dir)
            info("    ├── All original files moved to backup directory %s", orig_dir)
            merge_bin_files(game, REMOVEMODE)
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

games_to_merge = scan_directories(GAMEROOT)
process_games(games_to_merge, REMOVEMODE)

end_time = time.time()
runtime_seconds = int(end_time - start_time)
hours, remainder = divmod(runtime_seconds, 3600)
minutes, seconds = divmod(remainder, 60)
info("Script ended. Runtime: %02d:%02d:%02d (hh:mm:ss)", hours, minutes, seconds)
print(" ")

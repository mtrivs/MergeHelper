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

# Path and URL for binmerge script
BINMERGE_URL = "https://raw.githubusercontent.com/putnam/binmerge/master/binmerge"
BINMERGE_PATH = "./BinMerge.py"

# Configure logging for console (colorized) and file (plain text)
LOG_FILE = "mergehelper.log"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
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

class ColorizedFormatter(logging.Formatter):
    """
    Custom formatter to add colors to log levels and messages for console output.
    """
    def format(self, record):
        log_color = COLORS.get(record.levelname, COLORS["RESET"])
        levelname_colored = f"{log_color}{record.levelname}{COLORS['RESET']}"
        record.levelname = levelname_colored

        # Apply the same color to the message
        record.msg = f"{log_color}{record.msg}{COLORS['RESET']}"
        return super().format(record)

# Create logger for console output (colorized)
console_logger = logging.getLogger("ConsoleLogger")
console_logger.setLevel(logging.DEBUG if VERBOSE_LOGGING else logging.INFO)

# Create stream handler with colorized output for console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG if VERBOSE_LOGGING else logging.INFO)
stream_handler.setFormatter(ColorizedFormatter("%(levelname)s | %(message)s"))  # Colorized for console
console_logger.addHandler(stream_handler)

# Create logger for file output (plain text)
file_logger = logging.getLogger("FileLogger")
file_logger.setLevel(logging.DEBUG)

# Create file handler with plain text output for log file
if ENABLE_LOGGING:
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG if VERBOSE_LOGGING else logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))  # Plain text formatter for file
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
    info(" ** BEGIN dependency pre-check ** ")
    
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

    info(" ** FINISH Dependency pre-check ** ")

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

        # Stream binmerge output in real-time using subprocess
        command = ["python3", BINMERGE_PATH, cue_file_path, GAMENAME, "-o", GAMEDIR]
        detail("    ├── Executing command: %s", " ".join(command))

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Capture and log stdout and stderr in real-time
        for line in process.stdout:
            detail("    ├────── %s", line.strip())
        for line in process.stderr:
            fail("    ├────── %s", line.strip())

        process.wait()
        if process.returncode != 0:
            raise Exception(f"BinMerge failed with return code {process.returncode}")
        else:
            info("    ├── BinMerge completed successfully.")

        # Handle file removal based on REMOVEMODE
        if REMOVEMODE == "1":
            shutil.rmtree(orig_dir)
            info("    ├── Original multi-track bin files removed!")
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

def process_directories(GAMEROOT, NAMEBY, REMOVEMODE):
    """
    Process all sub-directories in the GAMEROOT.

    This function iterates through all sub-directories in the specified root directory (GAMEROOT),
    identifies directories containing BIN and CUE files, and attempts to merge multi-track BIN files
    into a single BIN/CUE pair using the binmerge module.

    Parameters:
        GAMEROOT (str): The root directory containing game folders with BIN/CUE files.
        NAMEBY (str): Determines how the merged BIN/CUE files are named. Options:
                      - "folder": Use the folder name.
                      - "cue": Use the CUE file name.
        REMOVEMODE (str): Specifies the behavior for handling original files after a successful merge.
                          Options:
                          - "0": No removal.
                          - "1": Remove original files if the merge is successful.
                          - "2": Prompt the user for action.

    Returns:
        None: The function performs operations directly on the file system and logs the results.
    """
    info(" ** BEGIN processing directories ** ")
    game_dirs = [entry for entry in os.scandir(GAMEROOT) if entry.is_dir()]
    for GAMEDIR in game_dirs:
        GAMEDIR = os.path.join(GAMEROOT, GAMEDIR)
        if os.path.isdir(GAMEDIR):
            info("Now processing %s", os.path.basename(GAMEDIR))
            files_in_dir = os.listdir(GAMEDIR)
            BINCOUNT = len([file for file in files_in_dir if file.lower().endswith(".bin")])
            CUECOUNT = len([file for file in files_in_dir if file.lower().endswith(".cue")])
            if CUECOUNT == 1:
                cue_files = [file for file in os.listdir(GAMEDIR) if file.lower().endswith(".cue")]
                if NAMEBY == "cue":
                    GAMENAME = os.path.splitext(cue_files[0])[0]  # Use CUE file name without extension
                else:
                    GAMENAME = os.path.basename(GAMEDIR)  # Use folder name
            elif CUECOUNT > 1:
                fail("    └── Multiple CUE files found in %s. Skipping merge.", GAMEDIR)
                detail("    └── CUE files found: %s", [file for file in files_in_dir if file.lower().endswith(".cue")])
                continue



            if BINCOUNT == 0:
                fail("    └── No BIN found for %s", GAMENAME)
                continue
            elif BINCOUNT == 1:
                warn("    └── No merge needed for %s", GAMENAME)
                continue
            elif BINCOUNT > 1:
                info("    ├── Multiple BIN files found.  Attempting merge for %s", GAMENAME)
                detail("    ├── Output filename determined by %s: %s", NAMEBY, GAMENAME)
                orig_dir = os.path.join(GAMEDIR, 'orig')
                if os.path.exists(orig_dir) and os.listdir(orig_dir):
                    fail("    └── Backup directory already exists and contains files. Skipping %s to avoid overwriting.", GAMEDIR)
                    continue
                os.makedirs(orig_dir, exist_ok=True)
                try:
                    cue_bin_files = [file for file in os.listdir(GAMEDIR) if file.lower().endswith(('.cue', '.bin'))]
                except PermissionError as exc:
                    fail("    └── Permission denied while accessing directory %s. Error: %s", GAMEDIR, exc)
                    continue
                except FileNotFoundError as exc:
                    fail("    └── Directory %s not found. Error: %s", GAMEDIR, exc)
                    continue
                except Exception as exc:
                    fail("    └── Failed to list files in directory %s. Error: %s", GAMEDIR, exc)
                    continue
                for file in cue_bin_files:
                    try:
                        shutil.move(os.path.join(GAMEDIR, file), orig_dir)
                        detail("    ├── Moved file %s to backup directory %s", file, orig_dir)
                    except OSError as exc:
                        fail("    └── Failed to move file %s to backup directory. Skipping file. Error: %s", file, exc)
                        continue
                info("    ├── All original files moved to backup directory %s", orig_dir)
                merge_bin_files(orig_dir, GAMEDIR, GAMENAME, REMOVEMODE)

    info(" ** FINISHED processing all directories ** ")


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
info("""
    ███╗░░░███╗███████╗██████╗░░██████╗░███████╗██╗░░██╗███████╗██╗░░░░░██████╗░███████╗██████╗░
    ████╗░████║██╔════╝██╔══██╗██╔════╝░██╔════╝██║░░██║██╔════╝██║░░░░░██╔══██╗██╔════╝██╔══██╗
    ██╔████╔██║█████╗░░██████╔╝██║░░██╗░█████╗░░███████║█████╗░░██║░░░░░██████╔╝█████╗░░██████╔╝
    ██║╚██╔╝██║██╔══╝░░██╔══██╗██║░░╚██╗██╔══╝░░██╔══██║██╔══╝░░██║░░░░░██╔═══╝░██╔══╝░░██╔══██╗   █░█ ▄█
    ██║░╚═╝░██║███████╗██║░░██║╚██████╔╝███████╗██║░░██║███████╗███████╗██║░░░░░███████╗██║░░██║   ▀▄▀ ░█
    ╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚═╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚══════╝╚══════╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝

                                https://github.com/mtrivs/MergeHelper
                                        Powered by BinMerge!
""")

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

process_directories(GAMEROOT, NAMEBY, REMOVEMODE)

end_time = time.time()
runtime_seconds = int(end_time - start_time)
hours, remainder = divmod(runtime_seconds, 3600)
minutes, seconds = divmod(remainder, 60)
info("Script ended. Runtime: %02d:%02d:%02d (hh:mm:ss)", hours, minutes, seconds)
print(" ")

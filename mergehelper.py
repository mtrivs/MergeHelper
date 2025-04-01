#!/usr/bin/env python3
# 'MergeHelper v1.0' by mtrivs
#
# This script facilitates batch conversion of multi-track disc images into a single BIN/CUE pair using the binmerge tool.
# It searches for folders containing more than one BIN file and merges them based on the data from the CUE sheet.
# The script will skip folders where no CUE files are present or if multiple CUE files are found in the same directory.
# If a merge operation fails, the script cleans up by restoring the original files.
#
# Copyright (C) 2024 Mitch Trivison (https://github.com/mtrivs)
# binmerge python script created by Chris Putnam (https://github.com/putnam/binmerge)
#
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Please report any bugs on GitHub: https://github.com/mtrivs/MergeHelper

import os
import sys
import shutil
import subprocess
import time
import logging
import argparse
import urllib.request

##############################################################################################
# START USER CONFIGURABLE VARIABLES
##############################################################################################

# Root directory containing game folders with BIN/CUE files to be merged.
DEFAULT_GAMEROOT = "roms"

# Path to the BinMerge.py script.
DEFAULT_BINMERGE_PATH = "./BinMerge.py"

# Path to the Python 3 binary.
DEFAULT_PYDIR = "python3"

# Determines how the merged BIN/CUE files are named: by folder name or CUE file name.
DEFAULT_NAMEBY = "folder"

# Determines whether original files are deleted after a successful merge.
# Options: "0" (no removal), "1" (remove if successful), "2" (prompt user).
DEFAULT_REMOVEMODE = "2"

# Enables or disables logging to a file.
DEFAULT_ENABLE_LOGGING = True

# Enables or disables detailed logging for debugging purposes.
DEFAULT_VERBOSE_LOGGING = True

##############################################################################################
# END USER CONFIGURABLE VARIABLES
##############################################################################################

# Parse command-line arguments
parser = argparse.ArgumentParser(description="MergeHelper Script")
parser.add_argument("--gameroot", default=DEFAULT_GAMEROOT, help="Root directory containing game folders")
parser.add_argument("--binmerge-path", default=DEFAULT_BINMERGE_PATH, help="Path to BinMerge.py script")
parser.add_argument("--pydir", default=DEFAULT_PYDIR, help="Path to the Python 3 binary")
parser.add_argument("--nameby", default=DEFAULT_NAMEBY, choices=["folder", "cue"], help="Naming method for merged files")
parser.add_argument("--removemode", default=DEFAULT_REMOVEMODE, choices=["0", "1", "2"], help="File removal mode after merge Options: 0 - no removal, 1 - remove if successful, 2 - prompt user")
parser.add_argument("--enable-logging", type=lambda x: x.lower() == "true", default=DEFAULT_ENABLE_LOGGING, help="Enable or disable logging to file")
parser.add_argument("--verbose-logging", type=lambda x: x.lower() == "true", default=DEFAULT_VERBOSE_LOGGING, help="Enable or disable verbose logging")
args = parser.parse_args()

# Assign variables based on command-line arguments or defaults
GAMEROOT = args.gameroot
BINMERGE_PATH = args.binmerge_path
PYDIR = args.pydir
NAMEBY = args.nameby
REMOVEMODE = args.removemode
ENABLE_LOGGING = args.enable_logging
VERBOSE_LOGGING = args.verbose_logging

# Configure logging
LOG_FILE = "mergehelper.log"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

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
    """Custom formatter to add colors to log levels."""
    def format(self, record):
        log_color = COLORS.get(record.levelname, COLORS["RESET"])
        record.levelname = f"{log_color}{record.levelname}{COLORS['RESET']}"
        return super().format(record)

# Create logger
logger = logging.getLogger("MergeHelper")
logger.setLevel(logging.DEBUG if VERBOSE_LOGGING else logging.INFO)

# Create stream handler with colorized output
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(ColorizedFormatter("%(levelname)s: %(message)s"))
logger.addHandler(stream_handler)

# Conditionally add file handler based on ENABLE_LOGGING variable
if ENABLE_LOGGING:
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(file_handler)

# Logging helper functions for different log levels.
def info(message, *args):
    """Log an info message."""
    logger.info(message, *args)

def detail(message, *args):
    """Log a debug message (used for verbose logging)."""
    if VERBOSE_LOGGING:
        logger.debug(message, *args)

def warn(message, *args):
    """Log a warning message."""
    logger.warning(message, *args)

def fail(message, *args):
    """Log an error message."""
    logger.error(message, *args)

# Function to check dependencies required by the script.
def check_dependencies():
    """Ensure all required dependencies are available."""
    info(" ** BEGIN dependency pre-check ** ")
    
    # Check Python version.
    if sys.version_info[0] < 3:
        fail("   [-] This script requires Python 3 or later.")
        sys.exit(1)
    info("   [+] Python version check passed")

    # Ensure BinMerge.py exists or download it if missing.
    if not os.path.exists(BINMERGE_PATH):
        info("   [-] BinMerge.py not found at %s. Attempting to download...", BINMERGE_PATH)
        try:
            binmerge_url = "https://raw.githubusercontent.com/putnam/binmerge/main/BinMerge.py"
            urllib.request.urlretrieve(binmerge_url, BINMERGE_PATH)
            info("   [+] Successfully downloaded BinMerge.py to %s", BINMERGE_PATH)
        except urllib.error.URLError as e:
            fail("   [-] Failed to download BinMerge.py due to a URL error: %s", e)
            sys.exit(1)
        except OSError as e:
            fail("   [-] Failed to download BinMerge.py due to an OS error: %s", e)
            sys.exit(1)
    else:
        info("   [+] BinMerge.py is available")

    info(" ** FINISH Dependency pre-check ** ")

# Check dependencies before processing directories.
try:
    # Dependency check or other critical operation
    check_dependencies()
except (urllib.error.URLError, OSError) as e:
    logger.error("Critical error: %s", e)
    sys.exit(1)

# Print script banner and initialize runtime tracking.
info(" ")
start_time = time.time()
detail("Script started at: %s", time.strftime('%Y-%m-%dT%H:%M:%S%z'))
print("""
        ███╗░░░███╗███████╗██████╗░░██████╗░███████╗██╗░░██╗███████╗██╗░░░░░██████╗░███████╗██████╗░
        ████╗░████║██╔════╝██╔══██╗██╔════╝░██╔════╝██║░░██║██╔════╝██║░░░░░██╔══██╗██╔════╝██╔══██╗
        ██╔████╔██║█████╗░░██████╔╝██║░░██╗░█████╗░░███████║█████╗░░██║░░░░░██████╔╝█████╗░░██████╔╝
        ██║╚██╔╝██║██╔══╝░░██╔══██╗██║░░╚██╗██╔══╝░░██╔══██║██╔══╝░░██║░░░░░██╔═══╝░██╔══╝░░██╔══██╗   █░█ ▄█
        ██║░╚═╝░██║███████╗██║░░██║╚██████╔╝███████╗██║░░██║███████╗███████╗██║░░░░░███████╗██║░░██║   ▀▄▀ ░█
        ╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚═╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚══════╝╚══════╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝

                                    https://github.com/mtrivs/MergeHelper
                                            Powered by BinMerge!
""")

# Handle user prompt for REMOVEMODE if not pre-configured.
if REMOVEMODE == "2":
    info(
        "The REMOVEMODE variable has not been configured. This determines whether the original files are deleted after a successful merge operation. Edit the REMOVEMODE variable inside the script to disable this prompt.\n"
        "Your options to proceed are:\n"
        "\tN     KEEP the original (non-merged) game files in the orig folder after the merge process has completed\n"
        "\tY     DELETE the original (non-merged) game files once the merge process has SUCCESSFULLY completed\n"
        "\tQ     QUIT the script\n"
        "                ******  PROCEED CAREFULLY! DELETING GAME FILES CANNOT BE UNDONE ******")
    DELETEFILES = input(
        "Would you like to delete the original game files if the merge process is successful? [y/n/q]: ").lower()
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


info(" ** BEGIN processing directories ** ")
# Loop through all sub-directories of the GAMEROOT.
for GAMEDIR in os.listdir(GAMEROOT):
    GAMEDIR = os.path.join(GAMEROOT, GAMEDIR)
    if os.path.isdir(GAMEDIR):
        # Count BIN and CUE files in the directory.
        BINCOUNT = len([file for file in os.listdir(GAMEDIR) if file.lower().endswith(".bin")])
        CUECOUNT = len([file for file in os.listdir(GAMEDIR) if file.lower().endswith(".cue")])

        GAMENAME = os.path.basename(GAMEDIR)

        # Use CUE file name for merged files if NAMEBY is set to "cue".
        if CUECOUNT == 1 and NAMEBY == "cue":
            GAMENAME = [file for file in os.listdir(GAMEDIR) if file.lower().endswith(".cue")][0]

        info("Now processing %s", GAMENAME)

        # Handle cases based on the number of BIN files.
        if BINCOUNT == 0:
            fail("    └── No BIN found for %s", GAMENAME)
            continue
        elif BINCOUNT == 1:
            warn("    └── No merge needed for %s", GAMENAME)
            continue
        elif BINCOUNT > 1:
            info("    ├── Multiple BIN files found.  Attempting merge for %s", GAMENAME)

            # Ensure only one CUE file exists in the directory.
            if CUECOUNT == 1:
                CUENAME = [file for file in os.listdir(GAMEDIR) if file.lower().endswith(".cue")][0]
                detail("    ├── Using CUE file: %s", GAMENAME)
            elif CUECOUNT > 1:
                fail("Multiple CUE files found! Skipping merge for %s. Fix the issues with this folder and run the script again!", GAMENAME)
                continue
            else:
                fail("No CUE file detected! Skipping merge for %s. Fix the issues with this folder and run the script again!", GAMENAME)
                continue

            # Create a backup directory for original files.
            orig_dir = os.path.join(GAMEDIR, 'orig')
            os.makedirs(orig_dir, exist_ok=True)
            if os.listdir(orig_dir):
                fail("    └── Failed to create backup directory. Skipping file %s", GAMENAME)
                continue

            # Backup original BIN/CUE files.
            try:
                cue_bin_files = [file for file in os.listdir(GAMEDIR) if file.lower().endswith(('.cue', '.bin'))]
                for file in cue_bin_files:
                    shutil.move(os.path.join(GAMEDIR, file), orig_dir)
                detail("    ├── Backing up original BIN/CUE files to %s", orig_dir)
            except OSError as exc:
                fail("    └── Failed to backup BIN/CUE files! Skipping file %s. %s", GAMENAME, exc)
                continue

            # Merge BIN/CUE files using BinMerge.
            detail("    ├── Merging BIN files with BinMerge")
            new_cue = [file for file in os.listdir(orig_dir) if file.lower().endswith(".cue")][0]
            try:
                merge_output = subprocess.check_output([PYDIR, BINMERGE_PATH, new_cue, GAMENAME, "-o", GAMEDIR])
                for line in merge_output.splitlines():
                    detail("    ├────── %s", line[7:].decode('utf-8'))
                if REMOVEMODE == "1":
                    shutil.rmtree(orig_dir)
                    detail("    ├── Original multi-track bin files removed!")
                else:
                    detail("    ├── Original multi-track files can be found in: %s", orig_dir)
                info("    └── BinMerge completed successfully for %s", GAMENAME)
            except subprocess.CalledProcessError as e:
                for line in e.output.splitlines():
                    fail("    ├────── %s", line[7:].decode('utf-8'))
                fail("    └── Merge failed! Removing any partial BIN/CUE files and moving original files back!")
                os.remove(os.path.join(GAMEDIR, "*.[cC][uU][eE],*.[bB][iI][nN]"))
                shutil.move(os.path.join(orig_dir, "*.[cC][uU][eE],*.[bB][iI][nN]"), GAMEDIR)
                os.rmdir(orig_dir)

info(" ** FINISHED processing all directories ** ")

# Calculate and log script runtime.
end_time = time.time()
runtime_seconds = int(end_time - start_time)
hours, remainder = divmod(runtime_seconds, 3600)
minutes, seconds = divmod(remainder, 60)
logger.info("Script ended. Runtime: %02d:%02d:%02d (hh:mm:ss)", hours, minutes, seconds)
info(" ")

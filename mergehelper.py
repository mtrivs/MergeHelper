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

##############################################################################################
# START USER CONFIGURABLE VARIABLES
##############################################################################################

# The 'GAMEROOT' variable specifies the root directory containing disc folders.
# Each game folder within the root directory should include .bin and .cue files needing to be merged.
# This must be modified to match your folder structure prior to executing this script for the first time.
GAMEROOT = "roms"

# The 'PYDIR' variable is used to specify the absolute path of your python binary.
# This must be python version 3!
PYDIR = "python3"

# The 'NAMEBY' variable is used to specify how the filename of the merged BIN/CUE files is determined.
# By default, the name of the folder containing BIN/CUE files is used as the name of the resulting merged files.
# Options: "cue" or "folder"
NAMEBY = "folder"

# The 'REMOVEMODE' variable is used to determine if the original BIN/CUE files should be deleted after a successful merge operation.
# Options: "0" (no removal), "1" (remove if successful), "2" (prompt user)
REMOVEMODE = "2"

# The 'LOGGING' variable is used to specify whether the script should log output to a mergehelper.log log file.
LOGGING = True

# The 'VERBOSE_LOGGING' variable controls whether detailed logging is enabled.
VERBOSE_LOGGING = True

##############################################################################################
# END USER CONFIGURABLE VARIABLES
##############################################################################################

# Colors for terminal output
COLORS = {
    "NOCOLOR": "\033[0m",
    "RED": "\033[1;31m",
    "GREEN": "\033[0;32m",
    "ORANGE": "\033[0;33m",
    "BLUE": "\033[0;34m",
    "PURPLE": "\033[0;35m",
    "CYAN": "\033[0;36m",
    "LIGHTGRAY": "\033[0;37m",
    "DARKGRAY": "\033[1;30m",
    "LIGHTRED": "\033[1;31m",
    "LIGHTGREEN": "\033[1;32m",
    "YELLOW": "\033[1;33m",
    "LIGHTBLUE": "\033[1;34m",
    "LIGHTPURPLE": "\033[1;35m",
    "LIGHTCYAN": "\033[1;36m",
    "WHITE": "\033[1;37m",
}

# Set the timestamp format for logging purposes
TSTAMP = time.strftime("%Y-%m-%dT%H:%M:%S%:z")

# Logging function for both coloring and logging
def log(color, sev, message, writetolog):
    """Function to print colorized script output and to a log file if LOGGING is True """
    print(f"{COLORS[color]}{message}{COLORS['NOCOLOR']}")
    if writetolog and LOGGING:
        with open("mergehelper.log", "a", encoding="utf-8") as logfile:
            logfile.write(f"{TSTAMP} | {sev} | {message}\n")

# Functions for different log levels with optional log file writing
def info(message, writetolog):
    """Function calling the log function with info severity and green text"""
    log("GREEN", "INFO", message, writetolog)

def detail(message, writetolog):
    """Function calling the log function with detail severity and cyan text"""
    if VERBOSE_LOGGING:
        log("CYAN", "DETAIL", message, writetolog)

def warn(message, writetolog):
    """Function calling the log function with warn severity and yellow text"""
    log("YELLOW", "WARN", message, writetolog)

def fail(message, writetolog):
    """Function calling the log function with fail severity and red text"""
    log("RED", "FAIL", message, writetolog)

# Define dependency check function
def check_dependencies():
    """Function check the dependencies used within the script"""
    info(" ** BEGIN dependency pre-check ** ", True)
    # Check Python version
    if sys.version_info[0] < 3:
        fail("   [-] This script requires Python 3 or later.", True)
        sys.exit(1)
    info("   [+] Python version check passed", True)
    # Download BinMerge if it does not already exist.
    if not os.path.exists("./BinMerge.py"):
        try:
            import urllib.request
            import urllib.error
        except ImportError as import_err:
            fail(f"   [-] Failed to import the necessary modules: {import_err}", True)
            sys.exit(1)
        # Check if urllib.request is available
        try:
            urllib.request.urlopen("https://www.google.com", timeout=1)
        except urllib.error.URLError as url_err:
            fail(f"   [-] Unable to connect to the internet to check for urllib.request module availability. {url_err}", True)
            sys.exit(1)
        info("   [+] urllib.request module available", True)
    info("   [+] BinMerge.py is available", True)
    info(" ** FINISH Dependency pre-check ** ", True)

info(" ", True)
# Capture start time
start_time = time.time()
detail(f"Script started at: {TSTAMP}", True)
print(f"""{COLORS['LIGHTPURPLE']}

        ███╗░░░███╗███████╗██████╗░░██████╗░███████╗██╗░░██╗███████╗██╗░░░░░██████╗░███████╗██████╗░
        ████╗░████║██╔════╝██╔══██╗██╔════╝░██╔════╝██║░░██║██╔════╝██║░░░░░██╔══██╗██╔════╝██╔══██╗
        ██╔████╔██║█████╗░░██████╔╝██║░░██╗░█████╗░░███████║█████╗░░██║░░░░░██████╔╝█████╗░░██████╔╝
        ██║╚██╔╝██║██╔══╝░░██╔══██╗██║░░╚██╗██╔══╝░░██╔══██║██╔══╝░░██║░░░░░██╔═══╝░██╔══╝░░██╔══██╗   █░█ ▄█
        ██║░╚═╝░██║███████╗██║░░██║╚██████╔╝███████╗██║░░██║███████╗███████╗██║░░░░░███████╗██║░░██║   ▀▄▀ ░█
        ╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚═╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚══════╝╚══════╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝

                                    https://github.com/mtrivs/MergeHelper
                                            Powered by BinMerge!
{COLORS['NOCOLOR']}""")

# Check if user has selected whether to delete or save original game files
if REMOVEMODE == "2":
    info(
        "The REMOVEMODE variable has not been configured. This determines whether the original files are deleted after a successful merge operation. Edit the REMOVEMODE variable inside the script to disable this prompt.\n"
        "Your options to proceed are:\n"
        "\tN     KEEP the original (non-merged) game files in the orig folder after the merge process has completed\n"
        "\tY     DELETE the original (non-merged) game files once the merge process has SUCCESSFULLY completed\n"
        "\tQ     QUIT the script\n"
        "                ******  PROCEED CAREFULLY! DELETING GAME FILES CANNOT BE UNDONE ******", True)
    DELETEFILES = input(
        "Would you like to delete the original game files if the merge process is successful? [y/n/q]: ").lower()
    if DELETEFILES == 'y':
        REMOVEMODE = "1"
        info("Deleting original multi-track files after successful merge operation", True)
    elif DELETEFILES == 'n':
        REMOVEMODE = "2"
        info("Original BIN/CUE files will be backed up to a new 'orig' folder prior to merge operations", True)
    elif DELETEFILES == 'q':
        fail("User aborted script....", True)
        sys.exit(1)
    else:
        fail("Unknown response.  Run the script again and select a valid option", True)
        sys.exit(1)

# Check the dependencies of the script before going further
check_dependencies()

info(" ** BEGIN processing directories ** ", True)
# Loop through all sub-directories of the GAMEROOT
for GAMEDIR in os.listdir(GAMEROOT):
    GAMEDIR = os.path.join(GAMEROOT, GAMEDIR)
    if os.path.isdir(GAMEDIR):
        # Determine the number of BIN/CUE files inside Game directory
        BINCOUNT = len([file for file in os.listdir(GAMEDIR) if file.lower().endswith(".bin")])
        CUECOUNT = len([file for file in os.listdir(GAMEDIR) if file.lower().endswith(".cue")])

        GAMENAME = os.path.basename(GAMEDIR)

        # If a CUE file exists and the NAMEBY variable is set to `cue` above
        if CUECOUNT == 1 and NAMEBY == "cue":
            # Determine the name of the game from the CUE file name
            GAMENAME = [file for file in os.listdir(GAMEDIR) if file.lower().endswith(".cue")][0]

        # Display the game name being processed
        info(f"Now processing {GAMENAME}", True)

        # Check the number of BIN files
        if BINCOUNT == 0:
            # No BIN files found
            fail(f"    └── No BIN found for {GAMENAME}", True)
            continue
        elif BINCOUNT == 1:
            # Game folder only has 1 BIN file, so there is nothing to merge.
            warn(f"    └── No merge needed for {GAMENAME}", True)
            continue
        elif BINCOUNT > 1:
            info(f"    ├── Multiple BIN files found.  Attempting merge for {GAMENAME}", True)

            # Make sure there is only 1 CUE file inside the game directory
            if CUECOUNT == 1:
                CUENAME = [file for file in os.listdir(GAMEDIR) if file.lower().endswith(".cue")][0]
                detail(f"    ├── Using CUE file: {GAMENAME}", True)
            elif CUECOUNT > 1:
                fail(f"Multiple CUE files found! Skipping merge for {GAMENAME}. Fix the issues with this folder and run the script again!", True)
                continue
            else:
                fail(f"No CUE file detected! Skipping merge for {GAMENAME}. Fix the issues with this folder and run the script again!", True)
                continue

            # Make a backup (orig) directory inside the game directory
            orig_dir = os.path.join(GAMEDIR, 'orig')
            os.makedirs(orig_dir, exist_ok=True)
            if os.listdir(orig_dir):
                fail(f"    └── Failed to create backup directory. Skipping file {GAMENAME}", True)
                continue

            # Backup original BIN/CUE files
            try:
                # Use glob to match multiple file extensions
                cue_bin_files = [file for file in os.listdir(GAMEDIR) if file.lower().endswith(('.cue', '.bin'))]
                for file in cue_bin_files:
                    shutil.move(os.path.join(GAMEDIR, file), orig_dir)
                detail(f"    ├── Backing up original BIN/CUE files to {orig_dir}", True)
            except shutil.Error as shutil_err:
                fail(f"    └── Failed to backup BIN/CUE files! Skipping file {GAMENAME}. {shutil_err}", True)
                continue
            except FileNotFoundError as file_not_found_err:
                fail(f"    └── Failed to find BIN/CUE files in {GAMEDIR}. Skipping file {GAMENAME}. {file_not_found_err}", True)
                continue
            except Exception as exc:
                fail(f"    └── Failed to backup BIN/CUE files! Skipping file {GAMENAME}. {exc}", True)
                continue

            # Begin merging BIN/CUE files
            detail("    ├── Merging BIN files with BinMerge", True)
            new_cue = [file for file in os.listdir(orig_dir) if file.lower().endswith(".cue")][0]
            try:
                merge_output = subprocess.check_output([PYDIR, "./BinMerge.py", new_cue, GAMENAME, "-o", GAMEDIR])
                for line in merge_output.splitlines():
                    detail(f"    ├────── {line[7:].decode('utf-8')}", True)
                if REMOVEMODE == "1":
                    # Remove the original files
                    shutil.rmtree(orig_dir)
                    detail("    ├── Original multi-track bin files removed!", True)
                else:
                    detail(f"    ├── Original multi-track files can be found in: ${orig_dir}", True)
                info(f"    └── BinMerge completed successfully for {GAMENAME}", True)
            except subprocess.CalledProcessError as e:
                for line in e.output.splitlines():
                    fail(f"    ├────── {line[7:].decode('utf-8')}", True)
                fail("    └── Merge failed! Removing any partial BIN/CUE files and moving original files back!", True)
                os.remove(os.path.join(GAMEDIR, "*.[cC][uU][eE],*.[bB][iI][nN]"))
                shutil.move(os.path.join(orig_dir, "*.[cC][uU][eE],*.[bB][iI][nN]"), GAMEDIR)
                os.rmdir(orig_dir)

info(" ** FINISHED processing all directories ** ", True)
# Capture end time
end_time = time.time()

# Calculate runtime
runtime_seconds = int(end_time - start_time)
hours = runtime_seconds // 3600
minutes = (runtime_seconds % 3600) // 60
seconds = (runtime_seconds % 3600) % 60

# Print runtime
info(f"Script ended. Runtime: {hours:02d}:{minutes:02d}:{seconds:02d} (hh:mm:ss)", True)
info(" ", True)

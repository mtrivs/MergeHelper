#!/bin/bash
# 'MergeHelper v1.0' by mtrivs
# binmerge python script created by Chris Putnam (https://github.com/putnam/binmerge)
#
# This script facilitates batch conversion of multi-track disc images into a single BIN/CUE pair using the binmerge tool.
# It searches for folders containing more than one BIN file and merges them based on the data from the CUE sheet.
# The script will skip folders where no CUE files are present or if multiple CUE files are found in the same directory.
# If a merge operation fails, the script cleans up by restoring the original files.
#
# Requirements:
#   - Python 3 is required for binmerge to properly merge multi-track discs. Specify the Python 3 executable path in the PYDIR variable.
#   - Adjust the user-configurable options below according to your configuration.
#   - The root games directory should contain sub-folders for each disc, with each sub-folder containing BIN/CUE format files.
#
#   - Example GAMEROOT directory structure:
#   /home/mtrivs/games/                        # Set this directory as 'GAMEROOT' below (without the trailing forward slash '/')
#              +-- Some Multi-Track Game (USA)/
#              |      +-- Some Game (USA) (Track 1).bin
#              |      +-- Some Game (USA) (Track 2).bin
#              |      +-- Some Game (USA).cue
#              |
#              +-- Another Multi-Track Game (USA) (en, es, fr)/
#              |      +-- Another Game (USA) (en, es, fr) (Track 1).bin
#              |      +-- Another Game (USA) (en, es, fr) (Track 2).bin
#              |      +-- Another Game (USA) (en, es, fr).cue
#              |
#              +-- Previously Merged Game (USA)/
#                      +-- Previously Merged Game (USA).cue
#                      +-- Previously Merged Game (USA).bin
#                      +-- orig/                # See the 'REMOVEMODE' variable below
#                            +-- Previously Merged Game (USA) (Track 1).bin
#                            +-- Previously Merged Game (USA) (Track 2).bin
#                            +-- Previously Merged Game (USA).cue
##############################################################################################
#                     START USER CONFIGURABLE VARIABLES
##############################################################################################
#
# The 'GAMEROOT' variable specifies the root directory containing disc folders. Each game folder within the root directory should include
# .bin and .cue files needing to be merged.  See the crude example above.
# This must be modified to match your folder structure prior to executing this script for the first time.
#
# NOTE: This variable should not end with a forward slash '/'

GAMEROOT="roms"

# The 'PYDIR' variable is used to specify the absolute path of your python binary. This is typically installed in the system $PATH and should work
# by default, but may need to be modified on some systems to specify the version of python used to execute the script.
# This must be python version 3!
# If you do not set this variable, the script will call 'python3' by name

PYDIR="python3"

# The 'NAMEBY' variable is used to specify how the filename of the merged BIN/CUE files is determined.
# By default, the name of the folder containing BIN/CUE files is used as the name of the resulting merged files
#
# The variable can be optionally modified to one of the following values:
# NAMEBY="cue"    : Determine the resulting merged filename from the name of the cue sheet for the disc image
# NAMEBY="folder" : (default) Determine the resulting merged filename from the name of the folder containing the BIN/CUE files

NAMEBY="folder"

# The 'REMOVEMODE' variable is used to determine if the original BIN/CUE files should be deleted after a successful merge operation.
# By default, the ORIGINAL multi-BIN files will be moved to a new "orig" folder and will NOT be deleted
#
# The variable can be optionally modified to one of the following values:
# REMOVEMODE="0" : The script will NOT remove any original BIN/CUE files. Source files will be moved to a new 'orig' folder, created
#                  in the same directory as the BIN/CUE files
# REMOVEMODE="1" : The script WILL remove original BIN/CUE files only if the binmerge operation completes successfully.  Use with care!
# REMOVEMODE="2" : (default) Prompt user at start to determine if original BIN/CUE files should be removed after successful merge operation

REMOVEMODE="2"

# The 'LOGGING' variable is used to specify whether the script should log output to a mergehelper.log log file.  
# By default, a "mergehelper.log" file will be produced in the same directory as the script.
#
# The variable can be optionally modified to one of the following values:
# LOGGING="TRUE"  : (default) Create a mergehelper.log file with a log of the script output 
# LOGGING="FALSE" : Do not create a log file and display a log in the terminal only

LOGGING="TRUE"

# The 'VERBOSE_LOGGING' variable controls whether detailed logging is enabled.
# When set to "TRUE" or "true", detailed logging (such as each step in the merge process) will be written to the log file if logging is enabled.

VERBOSE_LOGGING="TRUE"

##############################################################################################
#                       END USER CONFIGURABLE VARIABLES
##############################################################################################
# Set up the colored script output
declare -A COLORS=(
    [NOCOLOR]='\033[0m'
    [RED]='\033[1;31m'
    [GREEN]='\033[0;32m'
    [ORANGE]='\033[0;33m'
    [BLUE]='\033[0;34m'
    [PURPLE]='\033[0;35m'
    [CYAN]='\033[0;36m'
    [LIGHTGRAY]='\033[0;37m'
    [DARKGRAY]='\033[1;30m'
    [LIGHTRED]='\033[1;31m'
    [LIGHTGREEN]='\033[1;32m'
    [YELLOW]='\033[1;33m'
    [LIGHTBLUE]='\033[1;34m'
    [LIGHTPURPLE]='\033[1;35m'
    [LIGHTCYAN]='\033[1;36m'
    [WHITE]='\033[1;37m'
)

# Set the timestamp format for logging purposes
TSTAMP=$(date +"%Y-%m-%dT%H:%M:%S%:z")

# Logging function for both coloring and logging
function log() {
    local color=$1
    local sev=$2
    local message=$3
    local writeToLog=${4}
    printf "${COLORS[$color]}%s${COLORS[NOCOLOR]}\n" "$message"
    if [[ "$writeToLog" == "log"  && ("$LOGGING" == "TRUE"  || "$LOGGING" == "true")]]; then
        echo "${TSTAMP} | $sev | $message" >> mergehelper.log
    fi
}

# Functions for different log levels with optional log file writing
function info() { log "GREEN" "   INFO   " "$1" "$2"; }
function detail() { [[ "$VERBOSE_LOGGING" == "TRUE" || "$VERBOSE_LOGGING" == "true" ]] && log "CYAN" "  DETAIL  " "$1" "$2"; }
function warn() { log "YELLOW" "   WARN   " "$1" "$2"; }
function fail() { log "RED" "   FAIL   " "$1" "$2"; }

info " " "log"
STARTSTAMP=$(date +%s)
detail "Script started at: ${TSTAMP}" "log"

echo -ne "${COLORS[LIGHTPURPLE]}"
cat << "EOF"

        ███╗░░░███╗███████╗██████╗░░██████╗░███████╗██╗░░██╗███████╗██╗░░░░░██████╗░███████╗██████╗░
        ████╗░████║██╔════╝██╔══██╗██╔════╝░██╔════╝██║░░██║██╔════╝██║░░░░░██╔══██╗██╔════╝██╔══██╗
        ██╔████╔██║█████╗░░██████╔╝██║░░██╗░█████╗░░███████║█████╗░░██║░░░░░██████╔╝█████╗░░██████╔╝
        ██║╚██╔╝██║██╔══╝░░██╔══██╗██║░░╚██╗██╔══╝░░██╔══██║██╔══╝░░██║░░░░░██╔═══╝░██╔══╝░░██╔══██╗   █░█ ▄█
        ██║░╚═╝░██║███████╗██║░░██║╚██████╔╝███████╗██║░░██║███████╗███████╗██║░░░░░███████╗██║░░██║   ▀▄▀ ░█
        ╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚═╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚══════╝╚══════╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝

                                    https://github.com/mtrivs/MergeHelper
                                            Powered by BinMerge!
EOF

# Check if user has selected whether to delete or save original game files
if [[ "$REMOVEMODE" == "2" ]]; then
    echo -e "${COLORS[NOCOLOR]}The ${COLORS[RED]}REMOVEMODE ${COLORS[NOCOLOR]}variable has not been configured. This determines whether the original files are deleted after a successful merge operation. Edit the ${COLORS[RED]}REMOVEMODE ${COLORS[NOCOLOR]}variable inside the script to disable this prompt.\n
Your options to proceed are:
\t${COLORS[GREEN]}N     KEEP${COLORS[NOCOLOR]} the original (non-merged) game files in the orig folder after the merge process has completed
\t${COLORS[RED]}Y     DELETE${COLORS[NOCOLOR]} the original (non-merged) game files once the merge process has ${COLORS[GREEN]}SUCCESSFULLY${COLORS[NOCOLOR]} completed
\t${COLORS[ORANGE]}Q     QUIT${COLORS[NOCOLOR]} the script\n"
    echo -e "${COLORS[RED]}                ******  PROCEED CAREFULLY! DELETING GAME FILES CANNOT BE UNDONE ******${COLORS[NOCOLOR]}"
    echo -en "Would you like to delete the original game files if the merge process is successful? [y/n/q]: "
	read -rn1 DELETEFILES
    echo -e "${COLORS[NOCOLOR]}"
    case "$DELETEFILES" in
        y|Y)
            REMOVEMODE="1"
            info "Deleting original multi-track files after successful merge operation" "log"
            ;;
        n|N)
            REMOVEMODE="2"
            info "Original BIN/CUE files will be backed up to a new 'orig' folder prior to merge operations" "log"
            ;;
        q|Q)
            fail "User aborted script...." "log"
            exit 1
            ;;
        *)
            fail "Unknown response.  Run the script again and select a valid option" "log"
            fail "User aborted script...." "log"
            exit 1
            ;;
    esac
fi

# Abort if any dependencies are missing
info "** BEGIN dependency pre-check **" "log"
DEPENDENCIES=("$PYDIR" "wget" "find" "mv" "chmod" "basename" "mkdir" "rm")
for DEPEND in "${DEPENDENCIES[@]}"; do
    if ! command -v "$DEPEND" &> /dev/null; then
        fail "  [-] The '$DEPEND' binary is required, but not available!" "log"
        fail "      Check your user permissions or try installing this package with your distribution's package manager" "log"
        fail "** FATAL ERROR - Script Exiting! **" "log"
        exit 1
    else
        info "   [+] $DEPEND command found!" "log"
    fi
done

# Check if BinMerge.py already exists
if [[ -f ./BinMerge.py ]]; then
    if [[ ! -x ./BinMerge.py ]]; then
        chmod +x ./BinMerge.py &> /dev/null || { fail "   [-] Unable to modify executable permissions for BinMerge.py!" "log"; fail "** FATAL ERROR - Script Exiting! **" "log"; exit 1; }
    fi
else
    detail "   [+] Downloading BinMerge.py from GitHub (URL: https://raw.githubusercontent.com/putnam/binmerge/master/binmerge)" "log"
    wget -q -O ./BinMerge.py https://raw.githubusercontent.com/putnam/binmerge/master/binmerge || { fail "      [-] Unable to download BinMerge.py from GitHub!" "log"; fail "** FATAL ERROR - Script Exiting! **" "log";  exit 1; }
    chmod +x ./BinMerge.py || { fail "      [-] Unable to modify permissions of BinMerge.py!" "log"; fail "** FATAL ERROR - Script Exiting! **" "log";  exit 1; }
fi

info "** FINISH Dependency pre-check **" "log"

# Loop through all sub-directories of the GAMEROOT
info "** BEGIN processing directories **" "log"
for GAMEDIR in "$GAMEROOT"/*; do
    if [[ -d "$GAMEDIR" ]]; then
        # Determine the number of BIN/CUE files inside Game directory
        BINCOUNT=$(find "$GAMEDIR" -maxdepth 1 -name "*.[bB][iI][nN]" | wc -l)
        CUECOUNT=$(find "$GAMEDIR" -maxdepth 1 -name "*.[cC][uU][eE]" | wc -l)

        GAMENAME=$(basename "$GAMEDIR")

        # If a CUE file exists and the NAMEBY variable is set to `cue` above
        if [[ "$CUECOUNT" -eq 1 && "$NAMEBY" == "cue" ]]; then
            # Determine the name of the game from the CUE file name
            GAMENAME=$(find "$GAMEDIR" -maxdepth 1 -type f -name "*.[cC][uU][eE]" -exec basename {} \;)
        fi

        # Display the game name being processed
        info "Now processing \"$GAMENAME\"" "log"

        # Check the number of BIN files
        if [[ "$BINCOUNT" -eq 0 ]]; then
            # No BIN files found
            fail "    └── No BIN found for \"$GAMENAME\"" "log"
            continue
        elif [[ "$BINCOUNT" -eq 1 ]]; then
            # Game folder only has 1 BIN file, so there is nothing to merge.
            warn "    └── No merge needed for \"$GAMENAME\"" "log"
            continue
        elif [[ "$BINCOUNT" -gt 1 ]]; then
            info "    ├── Multiple BIN files found.  Attempting merge" "log"
            
            # Make sure there is only 1 CUE file inside the game directory
            if [[ "$CUECOUNT" -eq 1 ]]; then
                CUENAME=$(find "$GAMEDIR" -maxdepth 1 -type f -name "*.[cC][uU][eE]" -exec basename {} \;)
                detail "    ├── Using CUE file: \"$CUENAME\"" "log"
            elif [[ "$CUECOUNT" -gt 1 ]]; then
                fail "Multiple CUE files found! Skipping merge for \"$GAMENAME\". Fix the issues with this folder and run the script again!" "log"
                continue
            else
                fail "No CUE file detected! Skipping merge for \"$GAMENAME\". Fix the issues with this folder and run the script again!" "log"
                continue
            fi
            
            # Make a backup (orig) directory inside the game directory
            if mkdir -p "$GAMEDIR/orig"; then
                detail "    ├── Backing up original BIN/CUE files to \"$GAMEDIR/orig\"" "log"
                if mv "$GAMEDIR"/*.{[cC][uU][eE],[bB][iI][nN]} "$GAMEDIR/orig/"; then
                    # Begin merging BIN/CUE files
                    detail "    ├── Merging BIN files with BinMerge" "log"
                    NEWCUE=$(find "$GAMEDIR/orig" -maxdepth 1 -name "*.[cC][uU][eE]")
                    
                    if MERGE_OUTPUT=$("$PYDIR" ./BinMerge.py "$NEWCUE" "$GAMENAME" -o "$GAMEDIR/"); then
                        # Merge completed successfully
                        while IFS= read -r BINOUT; do
                            detail "    ├────── ${BINOUT:7}" "log"
                        done <<< "$MERGE_OUTPUT"

                        if [[ "$REMOVEMODE" -eq 1 ]]; then
                            # Remove the original files
                            rm -r "$GAMEDIR/orig"
                            detail "    ├── Original multi-track bin files removed!" "log"
                        else
                            detail "    ├── Original multi-track files can be found in: \"$GAMEDIR/orig\"" "log"
                        fi
                        info "    └── BinMerge completed successfully for \"$GAMENAME\"" "log"
                    else
                        # Merge process failed
                        while IFS= read -r BINOUT; do
                            fail "    ├────── ${BINOUT:7}" "log"
                        done <<< "$MERGE_OUTPUT"
                        fail "    └── Merge failed! Removing any partial BIN/CUE files and moving original files back!" "log"
                        rm "$GAMEDIR"/*.{[cC][uU][eE],[Bb][Ii][nN]} &> /dev/null
                        mv "$GAMEDIR"/orig/*.{[cC][uU][eE],[Bb][Ii][nN]} "$GAMEDIR/" && rm -r "$GAMEDIR"/orig
                        continue
                    fi
                else
                    # Failed to backup BIN/CUE files
                    fail "    └── Failed to backup BIN/CUE files! Skipping file" "log"
                    continue
                fi
            else
                # Failed to create backup directory
                fail "    └── Failed to create backup directory. Skipping file" "log"
                continue
            fi
        fi
    fi
done
info "** FINISHED processing all directories **" "log"
ENDSTAMP=$(date +%s)
RUNTIME=$((ENDSTAMP-STARTSTAMP))
HOURS=$((RUNTIME / 3600))
MINUTES=$(( (RUNTIME % 3600) / 60 ))
SECONDS=$(( (RUNTIME % 3600) % 60 ))
detail "Script ended at ${TSTAMP}. Runtime: $HOURS:$MINUTES:$SECONDS (hh:mm:ss)" "log"
info " " "log"

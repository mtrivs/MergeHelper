#!/bin/bash
# 'MergeHelper v0.8' by mtrivs
# Bash wrapper for binmerge to batch convert multi-track disc images to a single BIN/CUE pair
# binmerge python script created by @putnam (https://github.com/putnam/binmerge)
#
# Requirements:
#   - The root games directory should contain sub-folders for each disc
#   - Each disc sub-folder should contain image files
#   - Disc images should be in BIN/CUE format
#   - Example:
#   /my/game/root/     <-----THIS directory should be the 'GAMEROOT' (without the forward slash '/')
#              |--> Some Game (USA)/
#              |      |--> Some Game (USA) (Track 1).bin
#              |      |--> Some Game (USA) (Track 2).bin
#              |      |--> Some Game (USA).cue
#              |--> Another Game (USA) (en, es, fr)/
#              |      |--> Another Game (USA) (en, es, fr) (Track 1).bin
#              |      |--> Another Game (USA) (en, es, fr) (Track 2).bin
#              |      |--> Another Game (USA) (en, es, fr).cue
#              |--> Already Merged Game (USA)/
#		      |--> Already Merged Game (USA).cue
#		      |--> Already Merged Game (USA).bin
#		      |--> orig/     <-----IF you want to remove the original source files after being merged, check out the 'REMOVEMODE' variable below
#			     |--> Already Merged Game (USA).cue
#			     |--> Already Merged Game (USA) (Track 1).bin
#			     |--> Already Merged Game (USA) (Track 2).bin
##############################################################################################
#          Options
##############################################################################################
# Set the 'GAMEROOT' directory to the root directory of your game folders.
# NOTE: This variable should not end with a forward slash '/'
GAMEROOT="/home/mtrivs/games"

# Set the 'NAMEBY' variable to "cue" if you would like the game name determined by the CUE filename
# By default, the name of the game folder containing the BIN/CUE files is used as the game name
NAMEBY="folder"

# OPTIONAL: Set the 'PYDIR' variable below, to absolute location of your python executable.  May be required for certain configurations.
# This must be python version 3!
# If you do not set this variable, the script will call `python3` by name
PYDIR="python3"
  
# By default the ORIGINAL milti-BIN files will be stored in a new "orig" folder and will NOT be deleted
# If you uncomment line 168 below, the original BIN/CUE files will be deleted after a successful merge process

# BELOW HAS NOT BEEN IMPLEMENTED YET
# The 'REMOVEMODE' variable is used to determine if the original BIN/CUE files should be deleted after a successful merge operation.
# The variable can be optionally modified to one of the following values:
#REMOVEMODE="0" #: The script will not remove any original BIN/CUE files. Source files will be moved to a new 'orig' folder, created
                  #  in the same directory as the BIN/CUE files
#REMOVEMODE="1" #: The script to remove original BIN/CUE files, if the binmerge operation completes successfully
REMOVEMODE="2"  #: [default] Prompt once before the script is executed and ask if original BIN/CUE files should be removed after being merged


##############################################################################################
#     DO NOT EDIT BELOW THIS LINE
##############################################################################################
echo "~~~~~~~~~~~~~~~   MergeHelper v0.5  ~~~~~~~~~~~~~~~~~"
echo "~~~~~~~~~~~~~~~    - by mtrivs -    ~~~~~~~~~~~~~~~~~"
echo "~~~~~~~~~~~~~~  Powered by binmerge  ~~~~~~~~~~~~~~~~"

# Abort if Python version 3 is not installed
"$PYDIR" --version &> /dev/null
if [ $? -ne 0 ]; then
        echo "ERROR: Python version 3 is required, but not found!"
        echo "Try setting the PYDIR variable inside this script or installing it with your distribution's package manager"
        echo "....Aborting!"
        exit 1
fi

# Check if BinMerge.py already exists
if [[ -f ./BinMerge.py  ]]; then
        if [[ -x ./BinMerge.py ]]; then
                echo "Dependency pre-check complelte.  Python3 installed and BinMerge.py downloaded!"
        else
                echo "BinMerge.py is not executable.  Attempting to change permissions!"
                chmod +x ./BinMerge.py &> /dev/null
                if [[ -x ./BinMerge.py ]]; then
                        echo "Successfully modified permissions for BinMerge.py!"
                        echo "Dependency pre-check complelte.  Python3 installed and BinMerge.py downloaded!"
                else
                        echo "ERROR: Unable to modify permissions for BinMerge.py!"
                        echo "Correct this error and run the script again.....Aborting!"
                        exit 1
                fi
        fi
else
        echo "BinMerge.py does not exist!  Attempting to download it from GitHub (URL: https://raw.githubusercontent.com/putnam/binmerge/master/binmerge)"
        wget -O ./BinMerge.py https://raw.githubusercontent.com/putnam/binmerge/master/binmerge &> /dev/null
        if [[ -f ./BinMerge.py  ]]; then
                echo "Successfully downloaded BinMerge.py!"
                chmod +x ./BinMerge.py
                if [[ -x ./BinMerge.py ]]; then
                        echo "Dependency pre-check complelte.  Python3 installed and BinMerge.py downloaded!"
                else
                        echo "ERROR: Unable to modify permissions of BinMerge.py!"
                        echo "Correct this error and run the script again.....Aborting!"
                        exit 1
                fi
        else
                echo "ERROR: Unable to download BinMerge.py from GitHub!"
                echo "Please try downloading the file manually, renaming it to "BinMerge.py", and place it"
                echo "in the same directory as this script....Aborting!"
                exit 1
        fi
fi
# Loop through all sub-directories of the GAMEROOT
for GAMEDIR in  "$GAMEROOT"/* ; do
        if [ -d "$GAMEDIR" ]; then
                # Determine the number of BIN files inside Game directory
                BINCOUNT=(`find "$GAMEDIR" -maxdepth 1 -name "*.[bB][iI][nN]" | wc -l`)
                # Determine the number of CUE files inside Game directory
		CUECOUNT=(`find "$GAMEDIR" -maxdepth 1 -name "*.[cC][uU][eE]" | wc -l`)

		# If a CUE file exists and the NAMEBY variable is set to `cue` above
		if [ "$CUECOUNT" -eq 1 ] && [ "$NAMEBY" == "cue" ]; then
                       	# Determine the name of the game from the CUE file name
			GAMENAME=`find "$GAMEDIR" -maxdepth 1 -type f -name "*.[cC][uU][eE]" -exec basename {} \;`
		else
	                # Determine the name of the game from the folder name
			GAMENAME=$(basename "$GAMEDIR")
		fi

                # Display the game name being processed
                echo "Now processing: "$GAMENAME""

                # If there are no BIN files in the folder, skip it
                if [ "$BINCOUNT" -eq 0 ]; then
                        echo "    ERROR: unable to find any BIN files for "$GAMENAME".  Skipping folder!"
                        continue
	        # If there are two or more BIN files, proceed with the merge process
                elif [ "$BINCOUNT" -gt 1 ]; then
                        echo "    More than one BIN detected for "$GAMENAME", attempting BinMerge!"
                        # Make sure there is only 1 CUE file inside the game directory
                        if [ "$CUECOUNT" -eq 1 ]; then
                                CUENAME=`find "$GAMEDIR" -maxdepth 1 -type f -name "*.[cC][uU][eE]" -exec basename {} \;`
                                echo "    Found CUE file: "$CUENAME""
                        elif [ "$CUECOUNT" -gt 1 ]; then
                                echo "    ERROR: Too many CUE files detected! Skipping merge for "$GAMENAME"..."
                                continue
                        else
                                echo "    ERROR: No CUE file detected! Skipping merge for "$GAMENAME"..."
				continue
			fi
                        FAIL=0
                        # Make a backup (orig) directory inside the game directory or FAIL=1
                        eval mkdir -p "\"$GAMEDIR/orig\"" || FAIL=1
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure when creating bkup directory, now copy original BIN/CUE files to backup directory
                                echo "    Backing up original BIN/CUE files!"
                                eval mv "\"$GAMEDIR\""/*.{[cC][uU][eE],[bB][iI][nN]} "\"$GAMEDIR\""/orig/ || FAIL=1
                        else
                                echo "    ERROR: Failed to create backup directory! Skipping file"
                                continue
                        fi
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure when copying .bin/.cue to bkup.  Begin merging BIN/CUE files
                                echo "    Merging BIN files!"
				NEWCUE=`find "$GAMEDIR"/orig -maxdepth 1 -name "*.[cC][uU][eE]"`
                                eval "$PYDIR" ./BinMerge.py "\"$NEWCUE\"" "\"$GAMENAME\"" -o "\"$GAMEDIR\"/" || FAIL=1
                        else
                                echo "    ERROR: Failed to backup BIN/CUE files! Skipping file"
                                continue
                        fi
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure in the conversion process. Uncomment below to remove backup directory after sucessful BIN merge
                                echo "    BinMerge completed successfully!"
                                #eval rm -r "\"$GAMEDIR\""/orig
                        else
                                # Merge process failed. Remove any partial BIN/CUE files and restore original BIN/CUE from backup
                                echo "    ERROR: Merge failed! Removing any partial BIN/CUE files and moving original files back!"
                                eval rm "\"$GAMEDIR\""/*.{[cC][uU][eE],[Bb][Ii][nN]} &> /dev/null
                                eval mv "\"$GAMEDIR\""/orig/*.{[cC][uU][eE],[Bb][Ii][nN]} "\"$GAMEDIR\"/" && eval rm -r "\"$GAMEDIR\""/orig
                                continue
                        fi
                else
                        # Game folder only has 1 BIN file, so there is nothing to merge.
                        echo "    "$GAMENAME" doesn't need to be merged!"
                fi
        fi
done
echo "** FINISHED processing all directories! **"

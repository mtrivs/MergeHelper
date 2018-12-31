#!/bin/bash
# MergeHelper by mtrivs
# Batch helper to convert multi-track disc images to a single BIN/CUE file using binmerge by @putnam (https://github.com/putnam/binmerge)
#
#   - Set the 'GAMEROOT' directory to the root directory of your disc images.
#   - Disc images should be in BIN/CUE format.
#   - Each game should contain disc images a separate folder beneath the root games directory
#   - Example:
#   /home/mtrivs/MyGames/     <-----THIS directory should be your 'GAMEROOT' (without the forward slash '/')
#              |--> Some Game (USA)/
#              |      |--> Some Game (USA) (Track 1).bin
#              |      |--> Some Game (USA) (Track 2).bin
#              |      |--> Some Game (USA).cue
#              |--> Another Game (USA) (en, es, fr)/
#              |      |--> Another Game (USA) (en, es, fr) (Track 1).bin
#              |      |--> Another Game (USA) (en, es, fr) (Track 2).bin
#              |      |--> Another Game (USA) (en, es, fr).cue
#              *
#
# NOTE: This variable should not end with a forward slash '/'
GAMEROOT="/home/mtrivs/games"
#
# If the 'DESTRUCTMODE' variable is left unchanged, the user will be prompted at the start of the script to determine if the original BIN/CUE files
# should be deleted after a successfully binmerge operation. The variable can be optionally modified to one of the following values:
# --------------------
# DESTRUCTMODE="2" : [default] The user will be prompted each time the script is executed, to determine if original files should be removed
# DESTRUCTMODE="0" : The script will not remove any original BIN/CUE files.   Instead, original files will be moved to a new 'orig' folder, created
#                    in the same directory as the BIN/CUE files
# DESTRUCTMODE="1" : The script to remove original BIN/CUE files, if the binmerge operation completes successfully
DESTRUCTMODE="2"
#
# Optional: Set the 'PYDIR' variable below, to absolute location of your python executable
# This must be python version 3!
# If you do not set this variable, the script will call 'python3' by name
PYDIR="python3"
#
# DO NOT EDIT BELOW THIS LINE
# ____________________________________________________________________________________
echo "~~~~~~~~~~~~~~~   MergeHelper v0.5  ~~~~~~~~~~~~~~~~~"
echo "~~~~~~~~~~~~~~~    - by mtrivs -    ~~~~~~~~~~~~~~~~~"
echo "~~~~~~~~~~~~~~  Powered by binmerge  ~~~~~~~~~~~~~~~~"
# Query the user to determine if they wish to remove the original BIN/CUE files
if [ $DESTRUCTMODE -eq "2" ]; then
	echo "Destructmode is UNSET"
	sleep 30
elif [ $DESTRUCTMODE -eq "1" ]; then
	echo "Destructmode is TRUE"
	sleep 30
elif [ $DESTRUCTMODE -eq "0" ]; then
	echo "Destructmode is FALSE"
	sleep 30
else
	echo "Unable to detect destructmode"
	sleep 30
fi
# Abort if Python version 3 is not installed
"$PYDIR" --version &> /dev/null
if [ $? -ne 0 ]; then
        echo "ERROR: Python version 3 is required, but not found!"
        echo "Try setting the PYDIR variable inside this script or installing it with your distribution's package manager"
        echo "....Aborting!"
        exit
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
                        exit
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
                        exit
                fi
        else
                echo "ERROR: Unable to download BinMerge.py from GitHub!"
                echo "Please try downloading the file manually, renaming it to "BinMerge.py", and place it"
                echo "in the same directory as this script....Aborting!"
                exit
        fi
fi
# Loop through all sub-directories of the GAMEROOT
for GAMEDIR in  "$GAMEROOT"/* ; do
        if [ -d "$GAMEDIR" ]; then
                # Determine the number of BIN files inside Game directory
                numbin=(`find "$GAMEDIR" -maxdepth 1 -name "*.[bB][iI][nN]" | wc -l`)

                # Determine the name of the game from the folder name
                gamename=$(basename "$GAMEDIR")

                # Display the game name being processed
                echo "Now processing folder: "$GAMENAME""

                # If there are no BIN files in the folder, skip it
                if [ "$numbin" -eq 0 ]; then
                        echo "...ERROR: unable to find any BIN files in "$GAMENAME".  Skipping folder!"
                        continue
                fi

                # If there are two or more BIN files, proceed with the merge process
                if [ "$numbin" -gt 1 ]; then
                        echo "...More than one BIN detected for "$GAMENAME", attempting BinMerge!"
                        cuecheck=(`find "$GAMEDIR" -maxdepth 1 -name "*.[cC][uU][eE]" | wc -l`)
                        # Make sure there is only 1 CUE file inside the game directory
                        if [ "$cuecheck" -eq 1 ]; then
                                cuename=`find "$GAMEDIR" -maxdepth 1 -type f -name "*.[cC][uU][eE]" -exec basename {} \;`
                                echo "...CUE file found: "$cuename""
                        else
                                echo "...ERROR: No CUE file or too mand CUE files detected! Skipping merge for "$GAMENAME"..."
                                continue
                        fi
                        FAIL=0
                        # Make a backup ("bkup") directory inside the game directory or FAIL=1
                        eval mkdir -p "\"$GAMEDIR/orig\"" || FAIL=1
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure when creating bkup directory, now copy original BIN/CUE files to backup directory
                                echo "...Backing up original BIN/CUE files!"
                                eval mv "\"$GAMEDIR\""/*.{[cC][uU][eE],[bB][iI][nN]} "\"$GAMEDIR\""/orig/ || FAIL=1
                        else
                                echo "...ERROR: Failed to create backup directory! Skipping file"
                                continue
                        fi
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure when copying .bin/.cue to bkup.  Begin merging BIN/CUE files
                                echo "...Merging BIN files!"
				NEWQUEUE=`find "$GAMEDIR"/orig -maxdepth 1 -name "*.[cC][uU][eE]"`
                                eval "$PYDIR" ./BinMerge.py "\"$NEWQUEUE\"" "\"$GAMENAME\"" -o "\"$GAMEDIR\"/" || FAIL=1
                        else
                                echo "...ERROR: Failed to backup BIN/CUE files! Skipping file"
                                continue
                        fi
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure in the conversion process. Uncomment below to remove backup directory after sucessful BIN merge
                                echo "...BinMerge completed successfully!"
                                #eval rm -r "\"$GAMEDIR\""/orig
                        else
                                # Merge process failed. Uncomment below to remove any partial BIN/CUE files and restore original BIN/CUE from backup
                                echo "...ERROR: Merge failed! Removing any partial files and moving original files back!"
                                eval rm "\"$GAMEDIR\""/*.{[cC][uU][eE],[Bb][Ii][nN]} &> /dev/null
                                eval mv "\"$GAMEDIR\""/orig/*.{[cC][uU][eE],[Bb][Ii][nN]} "\"$GAMEDIR\"/" && eval rm -r "\"$GAMEDIR\""/orig
                                continue
                        fi
                else
                        # Game folder only has 1 BIN file, so there is nothing to merge.
                        echo "..."$GAMENAME" doesn't need to be merged!"
                fi
        fi
done
echo "** FINISHED processing all directories! **"

#!/bin/bash
# MergeHelper - Batch convert multi-track disc images to a single bin/cue file
#
#   - Set the "GAMEROOT" directory to the root directory of your disc images.
#   - Disc images should be in .bin/.cue format.
#   - Each game should contain their disc images in it's own folder beneath the root games directory
#     i.e., /home/mtrivs/MyGames/
#              |-- Some Game (USA)
#              |      |-- Some Game (USA) (Track 1).bin
#              |      |-- Some Game (USA) (Track 2).bin
#              |      |-- Some Game (USA).cue
#              |-- Another Game (USA) (en, es, fr)
#              |      |-- Another Game (USA) (en, es, fr) (Track 1).bin
#              |      |-- Another Game (USA) (en, es, fr) (Track 2).bin
#              |      |-- Another Game (USA) (en, es, fr).cue
#
# NOTE: This variable should not end with a forward slash "/"
GAMEROOT="/root/games"
#
# Set the "binmerge" variable below to the location of the binmerge python file
# Download this from https://github.com/putnam/binmerge
binmerge="/root/binmerge.py"
#
# Set the "pydir" variable below to the location of your python3 executable
# Download this with your distribution of choice and provide the absolute path
pydir="/usr/bin/python3"
#
# DO NOT EDIT BELOW THIS LINE
# ___________________________
echo "******************************************"
echo "*********** MergeHelper v0.5! ************"
echo "******************************************"
for GAMEDIR in "$GAMEROOT"/* ; do
        if [ -d "$GAMEDIR" ]; then
                # Determine the number of BIN file inside Game directory
                numbin=(`find "$GAMEDIR" -maxdepth 1 -name "*.[bB][iI][nN]" | wc -l`)

                # Determine the name of the game from the folder name
                gamename=$(basename "$GAMEDIR")

                # Display the game name being processed
                echo "Now processing folder: "$gamename""

                # If there are no BIN files in the folder, skip it
                if [ "$numbin" -eq 0 ]; then
                        echo "...ERROR: unable to find any BIN files in "$gamename".  Skipping folder!"
                        continue
                fi

                # If there are two or more BIN files, proceed with the merge process
                if [ "$numbin" -gt 1 ]; then
                        echo "...More than one BIN detected for "$gamename", attempting BinMerge!"
                        cuecheck=(`find "$GAMEDIR" -maxdepth 1 -name "*.[cC][uU][eE]" | wc -l`)
                        # Make sure there is only 1 CUE file inside the game directory
                        if [ "$cuecheck" -eq 1 ]; then
                                cuename=('find "$GAMEDIR" -maxdepth 1 -type f -name "*.[cC][uU][eE]" -exec basename {} \;')
                                echo "...CUE file found: "$cuename""
                        else
                                echo "...ERROR: No CUE file or too mand CUE files detected! Skipping merge for "$gamename"..."
                                continue
                        fi
                        FAIL=0
                        # Make a backup ("bkup") directory inside the game directory or FAIL=1
                        eval mkdir -p "\"$GAMEDIR/bkup\"" || FAIL=1
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure when creating bkup directory, now copy original BIN/CUE files to backup directory
                                echo "...Backing up original BIN/CUE files!"
                                eval mv "\"$GAMEDIR\""/*.{[cC][uU][eE],[bB][iI][nN]} "\"$GAMEDIR\""/bkup/ || FAIL=1
                        else
                                echo "...ERROR: Failed to create backup directory! Skipping file"
                                continue
                        fi
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure when copying .bin/.cue to bkup.  Begin merging BIN/CUE files
                                echo "...Merging BIN files!"
                                eval "$pydir" "$binmerge" "\"$cuename\"" "\"$gamename\"" -o "\"$GAMEDIR\"/" || FAIL=1
                        else
                                echo "...ERROR: Failed to backup BIN/CUE files! Skipping file"
                                continue
                        fi
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure in the conversion process. Uncomment below to remove backup directory after sucessful BIN merge
                                echo "...BinMerge completed successfully!"
                                #eval rm -r "\"$GAMEDIR\""/bkup
                        else
                                # Merge process failed. Uncomment below to remove any partial BIN/CUE files and restore original BIN/CUE from backup
                                echo "...ERROR: Merge failed! Your original files are safe in a backup directory!"
                                #eval rm "\"$GAMEDIR\""/*.{[cC][uU][eE],[Bb][Ii][nN]} &> /dev/null
                                #eval mv "\"$GAMEDIR\""/bkup/*.{[cC][uU][eE],[Bb][Ii][nN]} "\"$GAMEDIR\"/" && eval rm -r "\"$GAMEDIR\""/bkup
                                continue
                        fi
                else
                       # Game folder only has 1 BIN file, so there is nothing to merge.
                       echo "..."$gamename" doesn't need to be merged!"
                fi
        fi
done
echo "** FINISHED processing all directories! **"
echo "******************************************"

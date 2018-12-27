#!/bin/bash
# MergeHelper - Convert multi-track disc images to a single bin/cue file
#
# * Set the "games" directory to the root directory of your games.
# * Game disc images should be in .bin/.cue format.
# * Each game should contain their disc images in it's own folder beneath the root games directory
#  i.e., /home/mtrivs/MyGames/
#           |-- Some Game (USA)
#           |      |-- Some Game (USA) (Track 1).bin
#           |      |-- Some Game (USA) (Track 2).bin
#           |      |-- Some Game (USA).cue
#           |-- Another Game (USA) (en, es, fr)
#           |      |-- Another Game (USA) (en, es, fr) (Track 1).bin
#           |      |-- Another Game (USA) (en, es, fr) (Track 2).bin
#           |      |-- Another Game (USA) (en, es, fr).cue
#
# NOTE: This variable should not end with a forward slash "/"
GAMEROOT="/roms/MyGames"
#
# Set the location of the binmerge python file
# Download this from https://github.com/putnam/binmerge
binmerge="/root/binmerge.py"
# DO NOT EDIT BELOW THIS LINE
# ___________________________
indent() { sed 's/^/   /'; }
echo "MergeHelper 0.1!"
for GAMEDIR in "$GAMEROOT"/* ; do
        if [ -d "$GAMEDIR" ]; then
                # Determine if more than one bin file exists
                numbin=(`find "$GAMEDIR" -maxdepth 1 -name "*.[bB][iI][nN]" | wc -l`)

                # Determine the name of the game from the folder name
                gamename=$(basename "$GAMEDIR")

                # Display the game name being processed
                echo "Now processing: "$gamename""
                # If there are two or more bin files, combine them
                               
                if [ "$numbin" -gt 1 ]; then
                        echo "....More than one .bin detected for "$gamename", attempting BinMerge!" | indent
                        cuename=('find "$GAMEDIR" -maxdepth 1 -type f -name "*.[cC][uU][eE]" -exec basename {} \;')
                        FAIL=0
                        # Make a backup ("bkup") directory inside the game directory or FAIL=1
                        eval mkdir -p "\"$GAMEDIR/bkup\"" | indent || FAIL=1
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure when creating bkup directory, now copy .bin/.cue files to backup directory
                                echo "Backing up original BIN/CUE files!" | indent
                                eval mv "\"$GAMEDIR\""/*.{[cC][uU][eE],[bB][iI][nN]} "\"$GAMEDIR\""/bkup/ | indent || FAIL=1
                        else
                                # Creation of the backup directory failed with nothing to cleanup. Skip game & continue processing other games
                                echo "Failed to create backup directory! Skipping file" | indent
                                continue
                        fi
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure when copying .bin/.cue to bkup.  Begin merging BIN/CUE files
                                echo "Merging BIN files!" | indent
                                eval /usr/bin/python3 "$binmerge" "\"$cuename\"" "\"$gamename\"" -o "\"$GAMEDIR\"/" | indent || FAIL=1
                        else
                                # BIN/CUE file backup failed.  Skip game & continue processing other games.
                                echo "Failed to backup BIN/CUE files! Skipping file" | indent
                                continue
                        fi
                        if [ "$FAIL" -lt 1 ]; then
                                # No failure in the conversion process.  Remove backup directory.
                                echo "BinMerge completed successfully!" | indent
                                eval rm -r "\"$GAMEDIR\""/bkup | indent
                        else
                                # Merge process failed.  Remove any partial files and restore BIN/CUE from backup
                                echo "Merge failed! Your original files are in a backup directory and are being copied back!" | indent
                                eval rm "\"$GAMEDIR\""/*.{[cC][uU][eE],[Bb][Ii][nN]} &> /dev/null 
                                eval mv "\"$GAMEDIR\""/bkup/*.{[cC][uU][eE],[Bb][Ii][nN]} "\"$GAMEDIR\"/" | indent && eval rm -r "\"$GAMEDIR\""/bkup | indent
                                continue
                        fi
                else
                       # Game folder only has 1 BIN file, so there is nothing to merge.
                       echo ""$gamename" doesn't need to be merged!" | indent
                fi
        fi
done

echo "FINISHED processing all games!"

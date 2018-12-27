#!/bin/bash
# MergeHelper - Convert multi-track disc images to a single bin/cue file
#
# * Set the "games" directory to the root directory of your games.
# * Game disc images should be in .bin/.cue format.
# * Each game should contain their disc images in it's own folder beneath the root games directory
#  i.e., /root/MyGames/  
#                  |--Castlevania SOTN (USA)/
#                  |  |--Castlevania SOTN (USA) (Track 1).bin
#                  |  |--Castlevania SOTN (USA) (Track 2).bin
#                  |  |--Castlevania SOTN (USA).cue
#                  |
#                  |--Some Other Game(USA)/
#
# NOTE: This variable should not end with a forward slash "/"
games="/roms/MyGames"
#
# Set the location of the binmerge python file
# Download this from https://github.com/putnam/binmerge
binmerge="/root/binmerge.py"
# DO NOT EDIT BELOW THIS LINE
# ___________________________
#count=0
echo "MergeHelper 0.1!"
for d in "$games"/* ; do
        if [ -d "$d" ]; then
                # Determine if more than one bin file exists
                numbin=(`find "$d" -maxdepth 1 -name "*.[bB][iI][nN]" | wc -l`)

                # Determine the name of the game from the folder name
                gamename=$(basename "$d")

                # Display the game name being processed
                echo "Now processing: "$gamename""
                # If there are two or more bin files, combine them
                if [ "$numbin" -gt 1 ]; then
                        echo "....More than one .bin detected for "$gamename", attempting BinMerge!"
                        cuename="$d/bkup/$gamename.cue"
                        FAIL=0
                        #echo "....game dir \"$d\""
                        #echo "....game name \"$gamename\""
                        #echo "....cue name \"$cuename\""
                        #echo "....\"$d/bkup\""
                        eval mkdir -p "\"$d/bkup\"" || FAIL=1
                        if [ "$FAIL" -lt 1 ]; then
                                echo "....Backing up original BIN/CUE files!"
                                eval mv "\"$d\""/*.{[cC][uU][eE],[bB][iI][nN]} "\"$d\""/bkup/ || FAIL=1
                        else
                                echo "....Failed to create backup directory! Skipping file"
                                continue
                        fi
                        if [ "$FAIL" -lt 1 ]; then
                                echo "....Merging BIN files!"
                                eval /usr/bin/python3 "$binmerge" "\"$cuename\"" "\"$gamename\"" -o "\"$d\"/" || FAIL=1
                        else
                                echo "....Failed to make backup BIN/CUE files! Skipping file"
                                continue
                        fi
                        if [ "$FAIL" -lt 1 ]; then
                                echo "....BinMerge completed successfully!"
                                eval rm -r "\"$d\""/bkup
                        else
                                echo "....Merge failed! Your original files are in a backup directory and will be copied back!"
                                eval rm "\"$d\""/*.{[cC][uU][eE],[Bb][Ii][nN]} &> /dev/null
                                eval mv "\"$d\""/bkup/*.{[cC][uU][eE],[Bb][Ii][nN]} "\"$d\"/" && eval rm -r "\"$d\""/bkup
                                continue
                        fi
                else
                        echo "...."$gamename" doesn't need to be merged!"
                fi
        fi
done

echo "FINISHED processing all games!"

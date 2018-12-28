# MergeHelper
A bash helper script that uses the [binmerge](https://github.com/putnam/binmerge) python script by [@putnam](https://github.com/putnam) to batch convert multi-track bin files to a single BIN/CUE pair.   This is commonly needed for PSX disc images with multiple tracks and works great for ReDump sets. 

In order for this script to work correctly, each game must be in its own directory.  The script supports spaces and special characters in folders and file names. For example:
```
/home/mtrivs/MyGames/
            |-- Some Game (USA)
            |      |-- Some Game (USA) (Track 1).bin
            |      |-- Some Game (USA) (Track 2).bin
            |      |-- Some Game (USA).cue
            |-- Another Game (USA) (en, es, fr)
            |      |-- Another Game (USA) (en, es, fr) (Track 1).bin
            |      |-- Another Game (USA) (en, es, fr) (Track 2).bin
            |      |-- Another Game (USA) (en, es, fr).cue
```

## What does MergeHelper do?
This script will search a directory and detect sub-folders containing more than one BIN file.   If more than one BIN file is detected, the original BIN files will be moved to a ./bkup folder wherever the game folder exists.   The script will then execute the Python script BinMerge, to combine the multiple BIN files into a single BIN/CUE file.    If the merge process is successful, the original files will be removed, leaving only the combined BIN/CUE files in your game folder.  If there is a problem with making a backup of your files before the merge process kicks off, the script will skip that file and continue processing other titles.   

## How do I use this script?
There are some items that need to be edited before you can run the script for the first time

-
- 

## Is this safe to use?
I have tested this myself and did not experience any negative side effects.  However, this script does leave the possibility for something to go wrong and you should proceed with caution.  I shall not be liable for any negative side effects caused by this script.  Run it at your own risk!

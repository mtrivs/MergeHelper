# MergeHelper
A bash script that uses the BinMerge python script to batch convert multi-track bin files to a single bin/cue pair.   This is commonly needed for PSX disc images with multiple tracks and works great for ReDump sets. 

In order for this script to work correctly, each game must be in its own directory.  The script supports spaces and special characters in folders and file names. For example:
```
/home/mtrivs/MyGames/
|-- Some Game (USA)
      |-- Some Game (USA) (Track 1).bin
      |-- Some Game (USA) (Track 2).bin
      |-- Some Game (USA).cue
|-- Another Game (USA) (en, es, fr)
      |-- Another Game (USA) (en, es, fr) (Track 1).bin
      |-- Another Game (USA) (en, es, fr) (Track 2).bin
      |-- Another Game (USA) (en, es, fr).cue
```

# What does MergeHelper do?
This script will search a directory and detect sub-folders containing more than one BIN file.   If more than one BIN file is detected, the original BIN files will be moved to a ./bkup folder wherever the game folder exists.   The script will then execute the Python script BinMerge, to combine the multiple BIN files into a single BIN/CUE file.    If the merge process is successful, the original files will be removed, leaving only the combined BIN/CUE files in your game folder.  If there is a problem with making a backup of your files before the merge process kicks off, the script will skip that file and continue processing other titles.   

# How do I use this script?
There are two items that need to be edited before you can run the script for the first time:


# Is this safe to use?
I have tested this myself and did not experience any negative side effects.  However, you should proceed with caution.


# MergeHelper
MergeHelper is a bash helper script that uses the [binmerge](https://github.com/putnam/binmerge) Python script by [@Putnam](https://github.com/putnam) to batch convert multi-track BIN files to a single BIN/CUE pair. This is commonly needed for PSX disc images with multiple tracks and works great for ReDump sets, but can be used in other applications where a single BIN/CUE pair is desired.

Combining multiple bin files is often necessary for PlayStation (PSX) games due to the use of Compact Disc Digital Audio (CDDA) for audio tracks. Each audio track is typically stored as a separate audio track alongside the main data track to ensure proper synchronization with gameplay. Game data may also be split across multiple tracks for distribution, either due to size limitations or organizational considerations. When a disk containing multiple tracks is ripped, each track becomes a separate BIN file.  Merging these files into a single BIN/CUE pair simplifies management and usage. For emulation or preservation purposes, a unified representation ensures accuracy and compatibility across platforms. MergeHelper streamlines this process, facilitating the management and utilization of PSX disc images for various applications.

## Features
- Detects sub-folders containing more than one BIN file and merges them into a single BIN/CUE pair.
- Supports spaces and special characters in folder and file names.
- Moves original BIN/CUE files to a new 'orig' folder before performing the merge operation.
- Error handling to stop/revert processing upon errors (see [Safety Considerations](#safety) below)
- Colorized terminal.
- (optional) Removes original files after a successful merge, leaving only the combined BIN/CUE files.
- (optional) Logs all output to file.

## Installation
To use MergeHelper, follow these steps:
1. Clone the MergeHelper repository to your local machine.
2. Ensure Python3 and wget are installed on your system.
3. Make the MergeHelper script executable using the following command:

   ```bash
   chmod +x mergehelper.sh
   ```

## Usage

**Example directory structure:**
```
/home/mtrivs/games/                        # Set this directory as 'GAMEROOT' below (without the trailing forward slash '/')
         |-- Some Multi-Track Game (USA)/
         |     |-- Some Multi-Track Game (USA) (Track 1).bin
         |     |-- Some Multi-Track Game (USA) (Track 2).bin
         |     |-- Some Multi-Track Game (USA).cue
         |
         |-- Another Multi-Track Game (USA) (en, es, fr)/
         |     |-- Another Multi-Track Game (USA) (en, es, fr) (Track 1).bin
         |     |-- Another Multi-Track Game (USA) (en, es, fr) (Track 2).bin
         |     |-- Another Multi-Track Game (USA) (en, es, fr) (Track 3).bin
         |     |-- Another Multi-Track Game (USA) (en, es, fr) (Track 4).bin
         |     |-- Another Multi-Track Game (USA) (en, es, fr) (Track 5).bin
         |     |-- Another Multi-Track Game (USA) (en, es, fr).cue
         |
         |-- Previously Merged Game (USA)/
                |-- Previously Merged Game (USA).cue
                |-- Previously Merged Game (USA).bin
                |-- orig/                # See the 'REMOVEMODE' variable below
                     |-- Previously Merged Game (USA).cue
                     |-- Previously Merged Game (USA) (Track 1).bin
                     |-- Previously Merged Game (USA) (Track 2).bin
                     |-- Previously Merged Game (USA) (Track 3).bin
```
In the provided example, the top-level directory is `/home/mtrivs/games/`. This directory should be set as the value for the `GAMEROOT` variable in the MergeHelper script, without the trailing forward slash. Each game should be contained within its own subfolder within this directory. Correctly specifying this path enables MergeHelper to locate and process the game subfolders effectively.


To use MergeHelper:

1.  **Set the `GAMEROOT` Variable:** Edit the script and [modify the `GAMEROOT`](https://github.com/mtrivs/MergeHelper/blob/master/mergehelper.sh#L44) variable to point to the directory containing your game subfolders. To determine the `GAMEROOT` variable, look at the top-level directory that contains all your game subfolders.
    
2.  **Customize Additional Variables:** Customize any additional [variables](#vars) at the top of the script according to your requirements.
    
3.  **Run the Script:** Execute the script using the following command in your terminal:

   ```bash
   ./mergehelper.sh
   ```
<a id="vars"></a> 
## User Configurable Variables

MergeHelper includes several user-configurable variables at the top of the script that allow you to customize its behavior:

| Variable          | Description                                                                                           | Default Value |
| ----------------- | ----------------------------------------------------------------------------------------------------- | ------------- |
| `GAMEROOT`        | Root directory containing game subfolders. Each subfolder should contain the BIN/CUE files to merge. | `roms`        |
| `PYDIR`           | Absolute path of your Python 3 binary. By default the script assumes python3 is defined in the OS $PATH variable.                                                     | `python3`     |
| `NAMEBY`          | Determines how the filename of the merged BIN/CUE files is determined.<br>&nbsp;&nbsp;Options: `"folder"`, `"cue"`. | `folder`      |
| `REMOVEMODE`      | Specifies whether to delete original BIN/CUE files after a successful merge.<br>Options:<br>&nbsp;&nbsp;- `0`: The script will NOT remove any original BIN/CUE files. Source files will be moved to a new 'orig' folder, created in the same directory as the BIN/CUE files.<br>&nbsp;&nbsp;- `1`: The script will remove original BIN/CUE files only if the binmerge operation completes successfully.<br>&nbsp;&nbsp;- `2`: Prompt user at start to determine if original BIN/CUE files should be removed after successful merge operation. | `2`           |
| `LOGGING`         | Specifies whether to log output to a file. A `mergehelper.log` file will be created with all script output included.<br>&nbsp;&nbsp;Options: `TRUE`, `FALSE`.                                 | `TRUE`        |
| `VERBOSE_LOGGING` | Controls whether detailed logging is enabled. This option can be useful for debugging purposes.<br>&nbsp;&nbsp;Options: `TRUE`, `FALSE`.                                | `TRUE`        |

<a id="safety"></a>
## Safety Considerations
The script performs checks to detect and handle various error conditions gracefully, such as missing or inaccessible files, insufficient permissions, and unexpected behaviors during the merge process. Additionally, MergeHelper provides informative error messages and logging capabilities to aid in troubleshooting and resolving issues effectively. While MergeHelper has been tested and found to work reliably, it's important to proceed with caution. Some considerations:

- The script leaves the possibility for errors or unexpected behavior.
- It's recommended to perform operations in small batches until you are comfortable with the result.
- Back up important files before running the script to mitigate any potential risks.

**Disclaimer:** This script is provided as-is, without any warranty, express or implied. The author accepts no liability for any damages or issues arising from the use of this script. Users are advised to review and understand the script before running it and should proceed at their own risk.

## Troubleshooting

If you encounter any issues while using MergeHelper, refer to the following troubleshooting tips:
1. Ensure Python3 is installed, accessible from the command line, and properly defined in the `PYDIR` variable.
2. Check that the `GAMEROOT` variable in the script is correctly set to the directory containing your games. Each game should have its own subfolder, containing multiple BIN files and a single CUE file.
3. Review the script output or log file for important clues as to what is failing.

## License

MergeHelper is provided under the GNU General Public License (GPL) version 3.0 or later. See the [LICENSE](LICENSE) file for details.

![GPL Logo](https://www.gnu.org/graphics/gplv3-88x31.png)

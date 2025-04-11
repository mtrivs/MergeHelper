# MergeHelper
MergeHelper is a python helper script that uses the [binmerge](https://github.com/putnam/binmerge) Python script by [@Putnam](https://github.com/putnam) to batch convert multi-track BIN files to a single BIN/CUE pair. This is commonly needed for PSX disc images with multiple tracks and works great for ReDump sets, but can be used in other applications where a single BIN/CUE pair is desired.

## Features
- Detects cue files containing more than one BIN file and merges them into a single BIN/CUE pair.
- Supports spaces and special characters in folder and file names.
- Moves original BIN/CUE files to a new 'orig' folder before performing the merge operation.
- Error handling to stop/revert processing upon errors (see [Safety Considerations](#safety) below).
- Colorized terminal output and detailed logging options.
- Recursively scans directories under `GAMEROOT` to locate BIN/CUE files, even in nested subdirectories.
- Cross platform!

## Deprecation Notice
The Bash version of MergeHelper is now deprecated in favor of the Python version. The Python script provides enhanced functionality, including recursive directory scanning, better error handling, and improved logging. Users are encouraged to transition to the Python version for future use. The instructions below focus on the Python version.

# Quick Start Guide

Follow these steps to get started with MergeHelper:
1. **Ensure Python is Installed**  
   Verify that Python 3 is installed on your system. If Python is not installed, download and install it from the [official Python website](https://www.python.org/downloads/).

2. **Download the Script**  
   Download the `mergehelper.py` script from the following link and save it to your local machine:  
   [Download mergehelper.py](https://raw.githubusercontent.com/mtrivs/MergeHelper/main/mergehelper.py)

3. **Set the `GAMEROOT` Variable**  
   Edit the script and modify the `GAMEROOT` variable to point to the directory containing your game subfolders. For example:  
   ```python
   GAMEROOT = r"c:\my_roms"
   ```

4. **Customize Additional Variables**  
   Adjust other variables like `REMOVEMODE`, `ENABLE_LOGGING`, `VERBOSE_LOGGING`, and `PYDIR` as needed. Refer to the [User-Configurable Variables](#vars) section for details.

5. **Run the Script**  
   Execute the script using the following command in your terminal:  
   ```bash
   python3 mergehelper.py
   ```

6. **Follow Prompts**  
   If `REMOVEMODE` is set to `2` (default), the script will prompt you once at the start of the script to decide whether to delete original files after merging. Please read carefully to ensure you understand the options.

<a id="vars"></a>
## User-Configurable Variables

| Variable         | Description                                                                 | Default Value                                                                 |
|------------------|-----------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| `GAMEROOT`       | Root directory containing game folders with BIN/CUE files to be merged.     | ``         |
| `REMOVEMODE`     | Determines whether original files are deleted after a successful merge. Options: <ul><li>`0`: Do not delete original files after merging.</li><li> `1`: Automatically delete original files after merging.</li><li> `2`: Prompt the user once at the start of the script to decide.</li> |`2`|
| `ENABLE_LOGGING` | Enables or disables logging to a file.                                     | `True`                                                                       |
| `VERBOSE_LOGGING`| Enables or disables detailed logging for debugging purposes.               | `False`                                                                      |
| `PYDIR`          | Directory where Python is installed, if not in the system PATH.            | `python3`                                                           |

## Usage

### Example Directory Structure
```
/home/mtrivs/games/          # Set this directory as 'GAMEROOT'
├── Game A/
│   ├── Game A (Track 1).bin
│   ├── Game A (Track 2).bin
│   └── Game A.cue
├── Miscellaneous/
│   ├── Game B (Track 1).bin
│   ├── Game B (Track 2).bin
│   ├── Game B.cue
│   ├── Game C (Track 1).bin
│   ├── Game C (Track 2).bin
│   └── Game C.cue
└── Nested/
    ├── Game D/
    │   ├── Game D (Track 1).bin
    │   ├── Game D (Track 2).bin
    │   └── Game D.cue
    └── Subfolder/
        └── Game E/
            ├── Game E (Track 1).bin
            ├── Game E (Track 2).bin
            └── Game E.cue
```

The script will recursively scan all subdirectories under `GAMEROOT`, including nested directories such as `Game E`. In the above example, all "Game" files displayed will be merged in-place. This approach provides flexibility and ensures compatibility with complex folder structures.

### Notes
- Ensure that `GAMEROOT` is set to the correct root directory containing your game files.
- The script supports spaces and special characters in file and folder names.
- Original files will be moved to an `orig` folder before merging, ensuring a safe and reversible process.
- Setting the `REMOVEMODE` variable will delete the original game files from the orig folder upon successful merge.

<a id="safety"></a>
## Safety Considerations
The script performs checks to detect and handle various error conditions gracefully, such as missing or inaccessible files, insufficient permissions, and unexpected behaviors during the merge process. Additionally, MergeHelper provides informative error messages and logging capabilities to aid in troubleshooting and resolving issues effectively. While MergeHelper has been tested and found to work reliably, it's important to proceed with caution. Some considerations:

- The script leaves the possibility for errors or unexpected behavior.
- It's recommended to perform operations in small batches until you are comfortable with the result.
- Back up important files before running the script to mitigate any potential risks.

**Disclaimer:** This script is provided as-is, without any warranty, express or implied. The author accepts no liability for any damages or issues arising from the use of this script. Users are advised to review and understand the script before running it and should proceed at their own risk.

## Troubleshooting

If you encounter issues while using MergeHelper, follow these steps to diagnose and resolve the problem:

1. **Verify Python Installation**  
   Ensure Python 3 is installed and accessible from the command line. On Windows, the command is typically `python`, while on other operating systems, it is usually `python3`. Update the `PYDIR` variable in the script if Python is not in your system's PATH.

2. **Check `GAMEROOT` Configuration**  
   Confirm that the `GAMEROOT` variable in the script is correctly set to the directory containing your game files. 

3. **Check File Permissions**  
   Verify that the script has the necessary permissions to read, write, and modify files in the `GAMEROOT` directory and its subdirectories.

4. **Review Script Output and Logs**  
   Examine the script's terminal output or log file for error messages or warnings. Enable `VERBOSE_LOGGING` in the script to get detailed debugging information.

By following these steps, you should be able to identify and resolve most issues encountered while using MergeHelper.

## License

MergeHelper is provided under the GNU General Public License (GPL) version 3.0 or later. See the [LICENSE](LICENSE) file for details.

![GPL Logo](https://www.gnu.org/graphics/gplv3-88x31.png)

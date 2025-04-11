# MergeHelper
MergeHelper is a python helper script that uses the [binmerge](https://github.com/putnam/binmerge) Python script by [@Putnam](https://github.com/putnam) to batch convert multi-track BIN files to a single BIN/CUE pair. This is commonly needed for PSX disc images with multiple tracks and works great for ReDump sets, but can be used in other applications where a single BIN/CUE pair is desired.
## Features
- Automatically detects CUE files referencing multiple BIN files and merges them into a single BIN/CUE pair.
- Fully supports folder and file names containing spaces or special characters.
- Creates a backup of original BIN/CUE files in a dedicated `orig` folder before performing merge operations.
- Includes robust error handling to halt or revert processing in case of issues (refer to [Safety Considerations](#safety)).
- Provides colorized terminal output for better readability and detailed logging options for troubleshooting.
- Recursively scans all subdirectories under `GAMEROOT` to locate BIN/CUE files, ensuring compatibility with complex folder structures.
- Accurately parses CUE files to identify discs with multiple BIN files.
- Designed for cross-platform compatibility, ensuring functionality on Windows, macOS, and Linux systems.


## Deprecation Notice
The Bash version of MergeHelper has been deprecated in favor of the Python version. Since BinMerge itself is a Python script, the Bash version requires Python to function and lacks cross-platform compatibility. The Python version offers significant enhancements, including recursive directory scanning, robust error handling, and improved logging. Users are strongly encouraged to transition to the Python version for continued support and better functionality. The instructions provided below focus exclusively on the Python version.

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
/home/mtrivs/games/          # Set this directory as the 'GAMEROOT'
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

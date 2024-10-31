# Baldur's Gate 3 Linux Mod Manager

A simple command-line tool to manage mods for Baldur's Gate 3 on Linux. This tool helps you install and remove mods while maintaining the correct file structure and XML configurations.

## Features

- Install mods from .zip archives or .pak files
- Remove installed mods
- Display mod details before installation/removal
- Automatic synchronization of mod settings
- Interactive menu system
- Support for both compressed archives and loose files
- Confirmation prompts with mod details

## Prerequisites

- Python 3.6 or higher
- Baldur's Gate 3 installed via Steam on Linux
- Standard Linux file permissions for Steam directories

## Installation

1. Clone or download the script to your preferred location
2. Make the script executable:

```bash
chmod +x bg3_mod_installer.py
```

## Usage

### Running the Tool

```bash
./bg3_mod_installer.py
```

### Menu Options

1. **Install mod**: Install a new mod from a .zip file or .pak file
2. **Remove mod**: Remove an installed mod
3. **Exit**: Close the program

### Installing Mods

1. Select option 1 from the main menu
2. Enter the full path to your mod file (either .zip or .pak)
3. Review the mod details (if available)
4. Confirm the installation
5. The tool will:
   - Extract/copy the mod files to the correct location
   - Update the mod settings
   - Synchronize configurations

### Removing Mods

1. Select option 2 from the main menu
2. Choose a mod from the displayed list
3. Review the mod details
4. Confirm the removal
5. The tool will:
   - Remove the mod files
   - Update the mod settings
   - Synchronize configurations

## File Locations

The tool manages files in the following locations:

- Mod files: `~/.steam/steam/steamapps/compatdata/1086940/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios/Baldur's Gate 3/Mods/`
- Primary mod settings: `~/.steam/steam/steamapps/compatdata/1086940/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios/Baldur's Gate 3/PlayerProfiles/Public/modsettings.lsx`
- Secondary mod settings: `~/.steam/steam/userdata/<STEAM_ID>/1086940/modsettings.lsx`

## Supported Mod Formats

- `.zip` archives containing:
  - `.pak` file(s)
  - `info.json` with mod metadata
- Standalone `.pak` files

## Error Handling

The tool includes error handling for common issues:

- Invalid file paths
- Unsupported file types
- Missing mod information
- File permission issues
- XML parsing errors

If you encounter any errors, the tool will display a relevant error message and return to the main menu.

## Best Practices

1. Always backup your modsettings.lsx file before making changes
2. Use mod archives with proper info.json files when possible
3. Review mod details before confirming installation/removal
4. Verify the game works after each mod installation

## Troubleshooting

If you encounter issues:

- Verify file permissions in the Steam directories
- Check that the mod file is not corrupted
- Ensure the mod is compatible with your game version
- Check the paths match your Steam installation

## Limitations

- Does not handle mod load order management (yet)
- No automatic backup feature (yet)
- Cannot modify mod configurations
- Cannot verify mod compatibility

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - feel free to use and modify as needed.

## Acknowledgments

- Based on [burningcoffeetimetravel's Manually Modding Baldur's Gate 3 on Linux Guide](https://www.nexusmods.com/baldursgate3/mods/11131)
- Inspired by not being able to run BG3MM for myself

## Support

If you encounter any issues or have suggestions, please open an issue in the project repository.

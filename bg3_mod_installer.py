#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Dict, List


class BG3ModInstaller:
    def __init__(self):
        self.steam_path = Path.home() / ".steam/steam"
        self.game_id = "1086940"
        self.larian_path = self.steam_path / f"steamapps/compatdata/{self.game_id}/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios"
        self.steam_userdata = self.steam_path / "userdata"
        
        # Derived paths
        self.mods_path = self.larian_path / "Baldur's Gate 3/Mods"
        self.profile_modsettings = self.larian_path / "Baldur's Gate 3/PlayerProfiles/Public/modsettings.lsx"

    def get_steam_id(self):
        """Get the first Steam ID from userdata directory."""
        try:
            steam_ids = [d for d in os.listdir(self.steam_userdata) if d.isdigit()]
            if not steam_ids:
                raise Exception("No Steam ID found in userdata directory")
            return steam_ids[0]
        except Exception as e:
            print(f"Error finding Steam ID: {e}")
            sys.exit(1)

    def get_installed_mods(self) -> List[Dict]:
        """Get list of currently installed mods from modsettings.lsx."""
        try:
            tree = ET.parse(self.profile_modsettings)
            root = tree.getroot()
            mods = []
            
            for mod in root.findall(".//node[@id='ModuleShortDesc']"):
                mod_info = {}
                for attr in mod.findall("attribute"):
                    mod_info[attr.get('id')] = attr.get('value')
                mods.append(mod_info)
            
            return mods
        except Exception as e:
            print(f"Error reading installed mods: {e}")
            return []

    def remove_mod(self, mod_index: int):
        """Remove a mod by its index from the list."""
        try:
            installed_mods = self.get_installed_mods()
            if not (0 <= mod_index < len(installed_mods)):
                print("Invalid mod index")
                return False

            mod_to_remove = installed_mods[mod_index]
            mod_folder = mod_to_remove['Folder']

            pak_path = self.mods_path / f"{mod_folder}.pak"
            if pak_path.exists():
                pak_path.unlink()
                print(f"Removed pak file: {pak_path}")

            steam_id = self.get_steam_id()
            userdata_modsettings = self.steam_userdata / steam_id / self.game_id / "modsettings.lsx"

            for settings_path in [self.profile_modsettings, userdata_modsettings]:
                tree = ET.parse(settings_path)
                root = tree.getroot()
                
                mods_children = root.find(".//node[@id='Mods']/children")
                if mods_children is not None:
                    for mod in mods_children.findall("node[@id='ModuleShortDesc']"):
                        folder = mod.find("attribute[@id='Folder']")
                        if folder is not None and folder.get('value') == mod_folder:
                            mods_children.remove(mod)
                            break
                
                tree.write(settings_path, encoding="utf-8", xml_declaration=True)
                print(f"Updated {settings_path}")

            return True

        except Exception as e:
            print(f"Error removing mod: {e}")
            return False

    def create_mod_xml(self, mod_info):
        """Create XML structure for mod entry."""
        module = ET.Element("node")
        module.set("id", "ModuleShortDesc")
        
        attributes = {
            "Folder": mod_info["Folder"],
            "MD5": mod_info.get("MD5", ""),
            "Name": mod_info["Name"],
            "UUID": mod_info["UUID"],
            "Version64": str(mod_info.get("Version", "36028797018963968"))
        }
        
        for key, value in attributes.items():
            attr = ET.SubElement(module, "attribute")
            attr.set("id", key)
            attr.set("type", "LSString")
            attr.set("value", value)
            
        return module

    def update_modsettings(self, mod_info):
        """Update both modsettings.lsx files with new mod information."""
        steam_id = self.get_steam_id()
        userdata_modsettings = self.steam_userdata / steam_id / self.game_id / "modsettings.lsx"
        
        for settings_path in [self.profile_modsettings, userdata_modsettings]:
            try:
                tree = ET.parse(settings_path)
                root = tree.getroot()
                
                mods_children = root.find(".//node[@id='Mods']/children")
                if mods_children is None:
                    raise Exception("Mods children section not found in modsettings.lsx")
                
                new_module = self.create_mod_xml(mod_info)
                mods_children.append(new_module)
                
                tree.write(settings_path, encoding="utf-8", xml_declaration=True)
                print(f"Updated {settings_path}")
                
            except Exception as e:
                print(f"Error updating {settings_path}: {e}")
                sys.exit(1)

    def install_mod(self, mod_path):
        """Install a mod from a zip file or directory."""
        try:
            self.mods_path.mkdir(parents=True, exist_ok=True)
            
            if mod_path.suffix.lower() in ['.zip', '.rar', '.7z']:
                with zipfile.ZipFile(mod_path, 'r') as zip_ref:
                    pak_files = [f for f in zip_ref.namelist() if f.endswith('.pak')]
                    info_files = [f for f in zip_ref.namelist() if f.endswith('info.json')]
                    
                    if not pak_files:
                        raise Exception("No .pak files found in archive")
                    
                    for pak_file in pak_files:
                        zip_ref.extract(pak_file, self.mods_path)
                        print(f"Installed {pak_file} to mods directory")
                    
                    if info_files:
                        info_data = json.loads(zip_ref.read(info_files[0]))
                        if "Mods" in info_data and len(info_data["Mods"]) > 0:
                            self.update_modsettings(info_data["Mods"][0])
                    
            elif mod_path.suffix.lower() == '.pak':
                shutil.copy2(mod_path, self.mods_path)
                print(f"Installed {mod_path.name} to mods directory")
                
            else:
                raise Exception("Unsupported file type. Please provide a .zip archive or .pak file")
                
        except Exception as e:
            print(f"Error installing mod: {e}")
            sys.exit(1)

def display_menu():
    """Display the main menu and get user choice."""
    print("\nBaldur's Gate 3 Mod Manager")
    print("1. Install mod")
    print("2. Remove mod")
    print("3. Exit")
    while True:
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            if 1 <= choice <= 3:
                return choice
            print("Please enter a number between 1 and 3")
        except ValueError:
            print("Please enter a valid number")

def display_installed_mods(mods: List[Dict]):
    """Display installed mods and get user choice for removal."""
    print("\nInstalled Mods:")
    for i, mod in enumerate(mods):
        print(f"{i + 1}. {mod['Name']} ({mod['Folder']})")
    
    while True:
        try:
            choice = int(input("\nEnter the number of the mod to remove (0 to cancel): "))
            if choice == 0:
                return None
            if 1 <= choice <= len(mods):
                return choice - 1
            print(f"Please enter a number between 0 and {len(mods)}")
        except ValueError:
            print("Please enter a valid number")

def main():
    installer = BG3ModInstaller()
    
    while True:
        choice = display_menu()
        
        if choice == 1:  # Install mod
            mod_path = input("\nEnter the path to the mod file (.zip or .pak): ")
            try:
                installer.install_mod(Path(mod_path))
                print("Mod installation completed successfully!")
            except Exception as e:
                print(f"Error installing mod: {e}")
                
        elif choice == 2:  # Remove mod
            installed_mods = installer.get_installed_mods()
            if not installed_mods:
                print("No mods currently installed.")
                continue
                
            mod_index = display_installed_mods(installed_mods)
            if mod_index is not None:
                if installer.remove_mod(mod_index):
                    print("Mod removed successfully!")
                else:
                    print("Failed to remove mod.")
                    
        else:  # Exit
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
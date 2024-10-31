#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


class BG3ModInstaller:
    def __init__(self):
        self.steam_path = Path.home() / ".steam/steam"
        self.game_id = "1086940"
        self.larian_path = (
            self.steam_path
            / f"steamapps/compatdata/{self.game_id}/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios"
        )
        self.steam_userdata = self.steam_path / "userdata"

        self.mods_path = self.larian_path / "Baldur's Gate 3/Mods"
        self.profile_modsettings = (
            self.larian_path / "Baldur's Gate 3/PlayerProfiles/Public/modsettings.lsx"
        )

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

    def create_mod_xml(self, mod_info):
        """Create XML structure for mod entry."""
        module = ET.Element("node")
        module.set("id", "ModuleShortDesc")

        attributes = {
            "Folder": mod_info["Folder"],
            "MD5": mod_info.get("MD5", ""),
            "Name": mod_info["Name"],
            "UUID": mod_info["UUID"],
            "Version64": str(mod_info.get("Version", "36028797018963968")),
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
        userdata_modsettings = (
            self.steam_userdata / steam_id / self.game_id / "modsettings.lsx"
        )

        for settings_path in [self.profile_modsettings, userdata_modsettings]:
            try:
                tree = ET.parse(settings_path)
                root = tree.getroot()

                mods_children = root.find(".//node[@id='Mods']/children")
                if mods_children is None:
                    raise Exception(
                        "Mods children section not found in modsettings.lsx"
                    )

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

            if mod_path.suffix.lower() in [".zip", ".rar", ".7z"]:
                with zipfile.ZipFile(mod_path, "r") as zip_ref:
                    pak_files = [f for f in zip_ref.namelist() if f.endswith(".pak")]
                    info_files = [
                        f for f in zip_ref.namelist() if f.endswith("info.json")
                    ]

                    if not pak_files:
                        raise Exception("No .pak files found in archive")

                    for pak_file in pak_files:
                        zip_ref.extract(pak_file, self.mods_path)
                        print(f"Installed {pak_file} to mods directory")

                    if info_files:
                        info_data = json.loads(zip_ref.read(info_files[0]))
                        if "Mods" in info_data and len(info_data["Mods"]) > 0:
                            self.update_modsettings(info_data["Mods"][0])

            elif mod_path.suffix.lower() == ".pak":
                shutil.copy2(mod_path, self.mods_path)
                print(f"Installed {mod_path.name} to mods directory")

            else:
                raise Exception(
                    "Unsupported file type. Please provide a .zip archive or .pak file"
                )

        except Exception as e:
            print(f"Error installing mod: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Baldur's Gate 3 Mod Installer for Linux"
    )
    parser.add_argument(
        "mod_path", type=Path, help="Path to the mod file (.zip or .pak)"
    )
    args = parser.parse_args()

    installer = BG3ModInstaller()
    installer.install_mod(args.mod_path)
    print("Mod installation completed successfully!")


if __name__ == "__main__":
    main()

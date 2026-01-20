"""
This script reverses the group-folder repacking and restores a flat directory.

It expects a structure like:
    base_folder/00001/prefix_00001_0004.tif
    base_folder/00002/prefix_00002_0005.tif

All TIFF files found inside 5-digit group folders are moved back into:
    base_folder/

No files are renamed.
Group folders are left in place (empty if all files were moved).

Usage:
1. Set base_folder to the directory that contains the group subfolders.
2. Run the script once.
3. All TIFF files will be returned to the flat base folder.
"""

import os
import re
import shutil

# ---- Configuration ----
base_folder = "/Volumes/T7 Touch/Data_analysis/2025-3/20250923-Pt-dac/dac_rh2"
group_folder_pattern = r"\d{5}"   # folders like 00001, 00002, ...

moved = 0
skipped = 0

# ---- Scan group folders ----
for entry in os.listdir(base_folder):
    folder_path = os.path.join(base_folder, entry)

    # Only process 5-digit numeric folders
    if not os.path.isdir(folder_path):
        continue
    if not re.fullmatch(group_folder_pattern, entry):
        continue

    for fname in os.listdir(folder_path):
        if not fname.lower().endswith(".tif"):
            continue

        src = os.path.join(folder_path, fname)
        dst = os.path.join(base_folder, fname)

        if os.path.exists(dst):
            print(f"Destination exists, skipping: {dst}")
            skipped += 1
            continue

        shutil.move(src, dst)
        moved += 1
        print(f"Moved: {entry}/{fname} → {fname}")

print(f"\nDone. Moved {moved} files, skipped {skipped}.")
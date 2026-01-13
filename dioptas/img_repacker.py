"""
This script reorganizes a flat directory of TIFF images into a hierarchical
group-based folder structure suitable for the hierarchical diff scripts.

It expects filenames of the form:
    prefix_00001_0004.tif
    prefix_00001_0005.tif
where the middle 5-digit number is the group ID and the last 4-digit number is
the frame index.

All matching TIFF files in the base folder are moved into subfolders named
after their group ID, for example:
    base_folder/00001/prefix_00001_0004.tif
    base_folder/00001/prefix_00001_0005.tif

No files are renamed and no extra folders are created.

Usage:
1. Set base_folder to the directory containing the flat TIFF files.
2. Run the script once.
3. The directory will be converted into the structure expected by the
   hierarchical difference scripts.
"""
import os
import re
import shutil

# ---- Configuration ----
base_folder = "/Volumes/T7 Touch/Data_analysis/2025-2/20250709-melt-exp/xrd/P3_flat"
pattern = r'(.+?)_(\d{5})_(\d{4})\.tif'   # prefix_00004_0005.tif

# ---- Scan flat directory ----
files = [f for f in os.listdir(base_folder) if f.lower().endswith(".tif")]

moved = 0
skipped = 0

for fname in files:
    match = re.match(pattern, fname)
    if not match:
        print(f"Skipping (no match): {fname}")
        skipped += 1
        continue

    prefix, group_str, index_str = match.groups()

    # Create subfolder for this group
    group_folder = os.path.join(base_folder, group_str)
    os.makedirs(group_folder, exist_ok=True)

    src = os.path.join(base_folder, fname)
    dst = os.path.join(group_folder, fname)

    if os.path.exists(dst):
        print(f"Already exists, skipping: {dst}")
        skipped += 1
        continue

    shutil.move(src, dst)
    moved += 1
    print(f"Moved: {fname} → {group_str}/")

print(f"\nDone. Moved {moved} files, skipped {skipped}.")
import os
import re
import numpy as np
import tifffile

# ---- Configuration ----
base_folder = '/Volumes/T7 Touch/Data_analysis/2025-2/20250709-melt-exp/xrd/P3'  # folder that contains folders 0001, 0002, ...
output_diff_folder = os.path.join(base_folder, "diff_images")
output_diffdiff_folder = os.path.join(base_folder, "diff_of_diff_images")
pattern = r'(.+?)_(\d{5})_(\d{4})\.tif'  # e.g. prefix_00004_0005.tif

# ---- Create output folders ----
os.makedirs(output_diff_folder, exist_ok=True)
os.makedirs(output_diffdiff_folder, exist_ok=True)

# ---- Step 1: Build a mapping of group_id -> {index_str: filepath} ----
file_dict = {}

folder_names = sorted([f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))])

for folder_name in folder_names:
    folder_path = os.path.join(base_folder, folder_name)
    for fname in os.listdir(folder_path):
        if not fname.lower().endswith('.tif'):
            continue
        match = re.match(pattern, fname)
        if match:
            prefix, group_str, index_str = match.groups()
            file_dict.setdefault(group_str, {})[index_str] = os.path.join(folder_path, fname)

# ---- Step 2: Compute and save _0005 - _0004 within each group ----
group_ids = sorted(file_dict.keys())

for group_id in group_ids:
    files = file_dict[group_id]
    try:
        img4 = tifffile.imread(files['0004'])[::-1].astype(np.float32)
        img5 = tifffile.imread(files['0005'])[::-1].astype(np.float32)
        diff = np.clip(img5 - img4, 0, 50)

        # Save result (flip back)
        out_path = os.path.join(output_diff_folder, f'diff_{group_id}.tif')
        tifffile.imwrite(out_path, diff[::-1])
        print(f"Saved within-group diff: {out_path}")
    except KeyError:
        print(f"Missing _0004 or _0005 for group {group_id}, skipping.")

# ---- Step 3: Compute and save _0005 - previous _0005 between groups ----
for i in range(1, len(group_ids)):
    prev_id = group_ids[i - 1]
    curr_id = group_ids[i]
    try:
        img_prev = tifffile.imread(file_dict[prev_id]['0005'])[::-1].astype(np.float32)
        img_curr = tifffile.imread(file_dict[curr_id]['0005'])[::-1].astype(np.float32)
        diff = np.clip(img_curr - img_prev, 0, 50)

        # Save result (flip back)
        out_path = os.path.join(output_diffdiff_folder, f'diffdiff_{prev_id}_to_{curr_id}.tif')
        tifffile.imwrite(out_path, diff[::-1])
        print(f"Saved between-group diff: {out_path}")
    except KeyError:
        print(f"Missing _0005 in group {prev_id} or {curr_id}, skipping.")
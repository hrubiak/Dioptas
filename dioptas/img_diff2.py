import os
import re
import numpy as np
import tifffile

# ---- Configuration ----
base_folder = '/Volumes/T7 Touch/Data_analysis/2025-2/20250709-melt-exp/xrd/P3'
output_diff_folder = os.path.join(base_folder, "diff_images")
output_diffdiff_folder = os.path.join(base_folder, "diff_of_diff_images")

pattern = r'(.+?)_(\d{5})_(\d{4})\.tif'  # e.g. prefix_00004_0005.tif
clip_lo, clip_hi = 0, 50

# ---- Create output folders ----
os.makedirs(output_diff_folder, exist_ok=True)
os.makedirs(output_diffdiff_folder, exist_ok=True)

def read_tif_flipped(path: str) -> np.ndarray:
    return tifffile.imread(path)[::-1].astype(np.float32)

def write_tif_flip_back(path: str, arr: np.ndarray) -> None:
    tifffile.imwrite(path, arr[::-1])

# ---- Step 1: Build mapping group_id -> {index_str: filepath} ----
file_dict = {}

folder_names = sorted(
    [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]
)

for folder_name in folder_names:
    folder_path = os.path.join(base_folder, folder_name)
    for fname in os.listdir(folder_path):
        if not fname.lower().endswith('.tif'):
            continue
        match = re.match(pattern, fname)
        if match:
            prefix, group_str, index_str = match.groups()
            file_dict.setdefault(group_str, {})[index_str] = os.path.join(folder_path, fname)

# Sort groups numerically, but keep the original string ids for naming
group_ids = sorted(file_dict.keys(), key=lambda s: int(s))

# ---- Step 2: Compute and save within-group diff: _0005 - _0004 ----
img5_cache = {}  # group_id -> flipped float32 image for _0005 (if present)

for group_id in group_ids:
    files = file_dict[group_id]

    if '0005' in files:
        img5_cache[group_id] = read_tif_flipped(files['0005'])

    if '0004' not in files or '0005' not in files:
        print(f"Missing _0004 or _0005 for group {group_id}, skipping within-group diff.")
        continue

    img4 = read_tif_flipped(files['0004'])
    img5 = img5_cache[group_id]

    diff = np.clip(img5 - img4, clip_lo, clip_hi)

    out_path = os.path.join(output_diff_folder, f'diff_{group_id}.tif')
    write_tif_flip_back(out_path, diff)
    print(f"Saved within-group diff: {out_path}")

# ---- Step 3: Compute and save between-group diff: _0005(curr) - _0005(prev) ----
valid_groups = [gid for gid in group_ids if gid in img5_cache]

for i in range(1, len(valid_groups)):
    prev_id = valid_groups[i - 1]
    curr_id = valid_groups[i]

    img_prev = img5_cache[prev_id]
    img_curr = img5_cache[curr_id]

    diff = np.clip(img_curr - img_prev, clip_lo, clip_hi)

    out_path = os.path.join(output_diffdiff_folder, f'diffdiff_{prev_id}_to_{curr_id}.tif')
    write_tif_flip_back(out_path, diff)
    print(f"Saved between-group diff: {out_path}")
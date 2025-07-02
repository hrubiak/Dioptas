import os
import re
import numpy as np
import tifffile
import matplotlib.pyplot as plt

# ---- Configuration ----
tif_folder = "/Volumes/T7 Touch/Data_analysis/2025-2/20250624-melt-devel/xrd/heating/4-pulse"
output_diff_folder = os.path.join(tif_folder, "diff_images")
output_diffdiff_folder = os.path.join(tif_folder, "diff_of_diff_images")
pattern = r'(.+?)_(\d{5})_(\d{4})\.tif'  # matches name_00xx_00yy.tif

# ---- Create output directories ----
os.makedirs(output_diff_folder, exist_ok=True)
os.makedirs(output_diffdiff_folder, exist_ok=True)

# ---- Step 1: Group files ----
files = [f for f in os.listdir(tif_folder) if f.lower().endswith(".tif")]
group_dict = {}

for f in files:
    match = re.match(pattern, f)
    if match:
        base, group_str, index_str = match.groups()
        group_id = int(group_str)
        index_id = int(index_str)
        group_dict.setdefault(group_id, {})[index_id] = f

# ---- Step 2: Compute and save difference images ----
diff_images = []
group_ids = sorted(group_dict.keys())

for group_id in group_ids:
    group_files = group_dict[group_id]
    try:
        img2_path = os.path.join(tif_folder, group_files[2])
        img3_path = os.path.join(tif_folder, group_files[3])

        img2 = tifffile.imread(img2_path)[::-1].astype(np.float32)
        img3 = tifffile.imread(img3_path)[::-1].astype(np.float32)

        diff = np.clip(img3 - img2, 0, 50)
        diff_images.append(diff)

        # Save
        out_name = f'diff_{group_id:04d}.tif'
        tifffile.imwrite(os.path.join(output_diff_folder, out_name), diff)
        print(f"Saved group diff image: {out_name}")
    except KeyError:
        print(f"Group {group_id} missing index 2 or 3; skipping.")
        continue

# ---- Step 3: Compute and save difference-of-difference images ----
for i in range(len(diff_images) - 1):
    group_from = group_ids[i]
    group_to = group_ids[i + 1]

    diff_of_diff = np.clip(diff_images[i + 1] - diff_images[i], 0, 50)

    out_name = f'diffdiff_{group_from:04d}_to_{group_to:04d}.tif'
    tifffile.imwrite(os.path.join(output_diffdiff_folder, out_name), diff_of_diff)
    print(f"Saved diff-of-diff image: {out_name}")
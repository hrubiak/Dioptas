import os
import re
import numpy as np
import tifffile

# ---- Configuration ----
tif_folder = '/folder'
output_diff_folder = os.path.join(tif_folder, "diff_images")
output_diffdiff_folder = os.path.join(tif_folder, "diff_of_diff_images")

pattern = r'(.+?)_(\d{5})_(\d{4})\.tif'  # matches: name_#####_####.tif
clip_lo, clip_hi = 0, 50

# ---- Create output directories ----
os.makedirs(output_diff_folder, exist_ok=True)
os.makedirs(output_diffdiff_folder, exist_ok=True)

def read_tif_flipped(path: str) -> np.ndarray:
    """Read TIFF, flip vertically, return float32."""
    return tifffile.imread(path)[::-1].astype(np.float32)

def write_tif_flip_back(path: str, arr: np.ndarray) -> None:
    """Write TIFF after flipping vertically back to original orientation."""
    tifffile.imwrite(path, arr[::-1])

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
diff_group_ids = []  # only groups we successfully processed

for group_id in sorted(group_dict.keys()):
    group_files = group_dict[group_id]

    if 2 not in group_files or 3 not in group_files:
        print(f"Group {group_id} missing index 2 or 3; skipping.")
        continue

    img2_path = os.path.join(tif_folder, group_files[2])
    img3_path = os.path.join(tif_folder, group_files[3])

    img2 = read_tif_flipped(img2_path)
    img3 = read_tif_flipped(img3_path)

    diff = np.clip(img3 - img2, clip_lo, clip_hi)
    diff_images.append(diff)
    diff_group_ids.append(group_id)

    out_name = f'diff_{group_id:04d}.tif'
    write_tif_flip_back(os.path.join(output_diff_folder, out_name), diff)
    print(f"Saved group diff image: {out_name}")

# ---- Step 3: Compute and save difference-of-difference images ----
for i in range(len(diff_images) - 1):
    group_from = diff_group_ids[i]
    group_to = diff_group_ids[i + 1]

    diff_of_diff = np.clip(diff_images[i + 1] - diff_images[i], clip_lo, clip_hi)

    out_name = f'diffdiff_{group_from:04d}_to_{group_to:04d}.tif'
    write_tif_flip_back(os.path.join(output_diffdiff_folder, out_name), diff_of_diff)
    print(f"Saved diff-of-diff image: {out_name}")
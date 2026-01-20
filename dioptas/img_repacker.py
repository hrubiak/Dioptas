"""
Repack a flat folder of TIFFs into a hierarchical structure when the number of
exposures per shot varies across the dataset.

Assumed filename pattern:
    <prefix>_<SHOT:5digits>_<EXPOSURE:4digits>.tif
Example:
    sampleA_00017_0004.tif

What the script does:
1) Scans all .tif files in base_folder and parses shot_id and exposure_id.
2) Builds a map: shot_id -> sorted unique list of exposure indices found.
3) Determines how many exposures were collected for each shot (Nexp).
4) Creates output folders of the form:
       base_folder/Nexp_<N>/<SHOT_ID>/
   and moves that shot’s files into the corresponding folder.
5) If a shot’s exposures look incomplete or gappy (optional check), it can be
   routed into:
       base_folder/Nexp_incomplete/<SHOT_ID>/
   instead of a normal Nexp_<N> bucket.

How to use:
- Set base_folder to your flat directory containing TIFFs.
- Adjust allow_gaps and expected_start if desired.
- Run once. It will move files (no renaming).
"""

import os
import re
import shutil
from collections import defaultdict

# ---- Configuration ----
base_folder = '/Volumes/T7 Touch/Data_analysis/2025-3/20250923-Pt-dac/dac_rh2'
pattern = r"(.+?)_(\d{5})_(\d{4})\.tif"  # prefix_00017_0004.tif

# Gap handling:
# - If allow_gaps is False, shots with missing exposure indices are routed to Nexp_incomplete.
# - expected_start controls what the first exposure index "should" be (commonly 1 or 0).
allow_gaps = True
expected_start = 1  # set to 0 if your exposures start at 0000

# If True, only print what would happen, do not move files
dry_run = False

# Folder name for incomplete/gappy shots (used only when allow_gaps is False)
incomplete_bucket_name = "Nexp_incomplete"

# ---- Step 1: Scan and parse files ----
tif_files = [f for f in os.listdir(base_folder) if f.lower().endswith(".tif")]

shot_to_files = defaultdict(list)     # shot_id_str -> [fullpaths]
shot_to_exposures = defaultdict(set)  # shot_id_str -> {exposure_int}
skipped = []

for fname in tif_files:
    m = re.match(pattern, fname)
    if not m:
        skipped.append(fname)
        continue

    prefix, shot_str, exp_str = m.groups()
    shot_to_files[shot_str].append(os.path.join(base_folder, fname))
    shot_to_exposures[shot_str].add(int(exp_str))

if skipped:
    print(f"Skipping {len(skipped)} files that did not match pattern:")
    for s in skipped[:20]:
        print("  ", s)
    if len(skipped) > 20:
        print("  ...")

if not shot_to_files:
    raise RuntimeError("No TIFF files matched the expected pattern. Check 'pattern' and filenames.")

# ---- Step 2: Determine Nexp per shot and (optionally) detect gaps ----
def is_contiguous(exps_sorted, start_expected):
    """Return True if exposures are contiguous with step=1 starting at start_expected."""
    if not exps_sorted:
        return False
    if exps_sorted[0] != start_expected:
        return False
    return all((b - a) == 1 for a, b in zip(exps_sorted[:-1], exps_sorted[1:]))

shot_info = {}  # shot_str -> dict with exposures, nexp, is_contig, bucket
for shot_str, exps in shot_to_exposures.items():
    exps_sorted = sorted(exps)
    nexp = len(exps_sorted)
    contig = is_contiguous(exps_sorted, expected_start)

    if (not allow_gaps) and (not contig):
        bucket = incomplete_bucket_name
    else:
        bucket = f"Nexp_{nexp}"

    shot_info[shot_str] = {
        "exposures": exps_sorted,
        "nexp": nexp,
        "contiguous": contig,
        "bucket": bucket,
    }

# ---- Step 3: Print a summary before moving ----
print("\nSummary by shot:")
for shot_str in sorted(shot_info.keys(), key=lambda s: int(s)):
    info = shot_info[shot_str]
    flag = ""
    if not info["contiguous"]:
        flag = " (non-contiguous/gappy)"
    print(f"  Shot {shot_str}: Nexp={info['nexp']}, bucket={info['bucket']}{flag}")

# ---- Step 4: Move files into bucket/shot folders ----
moved = 0
already_there = 0
errors = 0

for shot_str in sorted(shot_info.keys(), key=lambda s: int(s)):
    bucket = shot_info[shot_str]["bucket"]
    dest_dir = os.path.join(base_folder, bucket, shot_str)

    if not dry_run:
        os.makedirs(dest_dir, exist_ok=True)

    for src_path in shot_to_files[shot_str]:
        fname = os.path.basename(src_path)
        dst_path = os.path.join(dest_dir, fname)

        # If it’s already in the right place (e.g., re-run), skip
        if os.path.abspath(src_path) == os.path.abspath(dst_path):
            already_there += 1
            continue

        if os.path.exists(dst_path):
            print(f"Destination exists, skipping: {dst_path}")
            errors += 1
            continue

        if dry_run:
            print(f"DRY RUN: would move {src_path} -> {dst_path}")
            moved += 1
        else:
            try:
                shutil.move(src_path, dst_path)
                moved += 1
            except Exception as e:
                print(f"Error moving {src_path} -> {dst_path}: {e}")
                errors += 1

print("\nDone.")
print(f"  Moved: {moved}")
print(f"  Already in place: {already_there}")
print(f"  Errors/skipped due to existing destination: {errors}")
print(f"  Unmatched filenames skipped: {len(skipped)}")
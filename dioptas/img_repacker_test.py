"""
TEST / DRY-RUN repacker (NO file moves, NO folder creation)

This script scans a flat folder of TIFFs and *reports* how it would group them
into a hierarchical structure when the number of exposures per shot varies.

Assumed filename pattern:
    <prefix>_<SHOT:5digits>_<EXPOSURE:4digits>.tif
Example:
    sampleA_00017_0004.tif

What it does (dry run):
1) Parses all matching TIFF files into (shot_id, exposure_id).
2) Determines how many exposures were collected for each shot (Nexp).
3) Optionally checks whether exposures are contiguous starting at expected_start.
4) Prints a summary:
     - shot -> exposures found -> Nexp -> bucket name (Nexp_<N> or Nexp_incomplete)
5) Prints the exact "would move" plan as source path -> destination path.

It does NOT:
- create any folders
- move/rename/copy any files
- modify anything on disk

Usage:
- Set base_folder to your flat TIFF directory.
- Adjust allow_gaps and expected_start if needed.
- Run and inspect the output.
"""

import os
import re
from collections import defaultdict

# ---- Configuration ----
base_folder = "/Volumes/T7 Touch/Data_analysis/2025-3/20250923-Pt-dac/dac_rh2"
pattern = r"(.+?)_(\d{5})_(\d{4})\.tif"  # prefix_00017_0004.tif

# Gap handling:
# - If allow_gaps is False, shots with missing exposure indices are routed to Nexp_incomplete.
# - expected_start controls what the first exposure index "should" be (commonly 1 or 0).
allow_gaps = True
expected_start = 1  # set to 0 if your exposures start at 0000

# Folder name for incomplete/gappy shots (used only when allow_gaps is False)
incomplete_bucket_name = "Nexp_incomplete"

# ---- Helpers ----
def is_contiguous(exps_sorted, start_expected):
    """True if exposures are contiguous with step=1 starting at start_expected."""
    if not exps_sorted:
        return False
    if exps_sorted[0] != start_expected:
        return False
    return all((b - a) == 1 for a, b in zip(exps_sorted[:-1], exps_sorted[1:]))

# ---- Step 1: Scan and parse files ----
tif_files = [f for f in os.listdir(base_folder) if f.lower().endswith(".tif")]

shot_to_files = defaultdict(list)     # shot_id_str -> [filenames]
shot_to_exposures = defaultdict(set)  # shot_id_str -> {exposure_int}
skipped = []

for fname in tif_files:
    m = re.match(pattern, fname)
    if not m:
        skipped.append(fname)
        continue

    prefix, shot_str, exp_str = m.groups()
    shot_to_files[shot_str].append(fname)
    shot_to_exposures[shot_str].add(int(exp_str))

if not shot_to_files:
    raise RuntimeError("No TIFF files matched the expected pattern. Check 'pattern' and filenames.")

# ---- Step 2: Compute Nexp per shot and bucket assignment ----
shot_info = {}
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

# ---- Step 3: Print summary ----
print("\n=== DRY RUN GROUPING SUMMARY ===")
print(f"Base folder: {base_folder}")
print(f"Pattern: {pattern}")
print(f"allow_gaps: {allow_gaps}, expected_start: {expected_start}\n")

for shot_str in sorted(shot_info.keys(), key=lambda s: int(s)):
    info = shot_info[shot_str]
    flag = "" if info["contiguous"] else " (non-contiguous/gappy)"
    print(f"Shot {shot_str}: Nexp={info['nexp']}, bucket={info['bucket']}{flag}")
    print(f"  exposures: {info['exposures']}")

print("\n=== WOULD-MOVE PLAN (no changes made) ===")
would_move_count = 0

for shot_str in sorted(shot_info.keys(), key=lambda s: int(s)):
    bucket = shot_info[shot_str]["bucket"]
    dest_dir = os.path.join(base_folder, bucket, shot_str)

    for fname in sorted(shot_to_files[shot_str]):
        src_path = os.path.join(base_folder, fname)
        dst_path = os.path.join(dest_dir, fname)
        print(f"{src_path}  ->  {dst_path}")
        would_move_count += 1

print(f"\nTotal matched TIFFs: {would_move_count}")
print(f"Unmatched TIFFs skipped: {len(skipped)}")

if skipped:
    print("\nFirst few skipped (pattern mismatch):")
    for s in skipped[:20]:
        print("  ", s)
    if len(skipped) > 20:
        print("  ...")
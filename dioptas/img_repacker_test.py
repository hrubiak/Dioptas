"""
Repack a flat folder of TIFFs into a 2-level hierarchy:

  base_folder/
    Nexp_<N>/          # N = number of exposures found for a shot (grouped by first index)
      Exp_<EEEE>/      # EEEE = exposure index (second index)
        <all matching tif files>

Assumed filename pattern:
    <prefix>_<SHOT:5digits>_<EXPOSURE:4digits>.tif
Example:
    sampleA_00017_0004.tif

What the script does:
1) Scans all .tif files and parses shot_id (first index) and exposure_id (second index).
2) Determines Nexp for each shot (count of unique exposure indices found for that shot).
3) Optionally (if allow_gaps=False) flags non-contiguous exposure sequences as "incomplete".
4) Moves each file into: base_folder/Nexp_<Nexp_for_shot>/Exp_<EXPOSURE>/.

No files are renamed.

Usage:
- Set base_folder.
- Set dry_run=True to preview without moving anything.
- Run once.
"""

import os
import re
import shutil
from collections import defaultdict

# ---- Configuration ----
base_folder = "/Volumes/T7 Touch/Data_analysis/2025-3/20250923-Pt-dac/dac_rh2"
pattern = r"(.+?)_(\d{5})_(\d{4})\.tif"  # prefix_00017_0004.tif

# If allow_gaps is False, shots whose exposures are not contiguous starting at expected_start
# will be routed to incomplete_bucket_name instead of Nexp_<N>.
allow_gaps = True
expected_start = 1  # set to 0 if exposure indices start at 0000

# If True, only print what would happen, do not move files or create folders
dry_run = False

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

# shot_str -> set(exposure_int)
shot_to_exposures = defaultdict(set)

# store parsed records so we don’t re-parse
# each record: (src_path, shot_str, exp_str)
records = []
skipped = []

for fname in tif_files:
    m = re.match(pattern, fname)
    if not m:
        skipped.append(fname)
        continue

    _prefix, shot_str, exp_str = m.groups()
    src_path = os.path.join(base_folder, fname)

    records.append((src_path, shot_str, exp_str))
    shot_to_exposures[shot_str].add(int(exp_str))

if skipped:
    print(f"Skipping {len(skipped)} files that did not match pattern:")
    for s in skipped[:20]:
        print("  ", s)
    if len(skipped) > 20:
        print("  ...")

if not records:
    raise RuntimeError("No TIFF files matched the expected pattern. Check 'pattern' and filenames.")

# ---- Step 2: Determine bucket (Nexp_*) for each shot ----
shot_to_bucket = {}

print("\nSummary by shot (used only to compute Nexp buckets):")
for shot_str in sorted(shot_to_exposures.keys(), key=lambda s: int(s)):
    exps_sorted = sorted(shot_to_exposures[shot_str])
    nexp = len(exps_sorted)
    contig = is_contiguous(exps_sorted, expected_start)

    if (not allow_gaps) and (not contig):
        bucket = incomplete_bucket_name
        flag = " (non-contiguous/gappy -> incomplete)"
    else:
        bucket = f"Nexp_{nexp}"
        flag = "" if contig else " (non-contiguous/gappy, but allowed)"

    shot_to_bucket[shot_str] = bucket
    print(f"  Shot {shot_str}: Nexp={nexp}, bucket={bucket}{flag}")

# ---- Step 3: Move files into Nexp_<N>/Exp_<exp>/ ----
moved = 0
already_there = 0
errors = 0

print("\nMove plan:")
for src_path, shot_str, exp_str in sorted(records, key=lambda r: (int(r[1]), int(r[2]))):
    bucket = shot_to_bucket[shot_str]
    dest_dir = os.path.join(base_folder, bucket, f"Exp_{exp_str}")
    fname = os.path.basename(src_path)
    dst_path = os.path.join(dest_dir, fname)

    # If it’s already in the right place (re-run), skip
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
        os.makedirs(dest_dir, exist_ok=True)
        try:
            shutil.move(src_path, dst_path)
            moved += 1
            print(f"Moved: {fname} -> {bucket}/Exp_{exp_str}/")
        except Exception as e:
            print(f"Error moving {src_path} -> {dst_path}: {e}")
            errors += 1

print("\nDone.")
print(f"  Moved: {moved}")
print(f"  Already in place: {already_there}")
print(f"  Errors/skipped due to existing destination: {errors}")
print(f"  Unmatched filenames skipped: {len(skipped)}")
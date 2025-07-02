import tifffile
import matplotlib.pyplot as plt
import numpy as np

# ---- Load TIFF ----
filename = "/Volumes/T7 Touch/Data_analysis/2025-2/20250624-melt-devel/xrd/heating/4-pulse/20250624-sam1_00035_0001.tif"
img = tifffile.imread(filename)

# ---- Optional Flip (match fabio[::-1]) ----
img_flipped = img[::-1]

# ---- Display ----
plt.figure(figsize=(8, 6))
plt.imshow(img_flipped, cmap='gray', vmin=np.percentile(img_flipped, 2), vmax=np.percentile(img_flipped, 98))
plt.colorbar(label='Counts')
plt.title("Flipped TIFF Image")
plt.show()
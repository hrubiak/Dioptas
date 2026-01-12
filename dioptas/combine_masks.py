from tifffile import TiffFile
from PIL import Image
import numpy as np
import shutil

original_path = '/Volumes/data/16idb/Data/Beamline/31 - Pilatus3 X CdTe 2M/Badpix_mask/badpix_mask_until181125.tif'
new_tif_path = 'badpix_mask_from181125.tif'
png_path = '/Volumes/data/16idb/Data/Beamline/31 - Pilatus3 X CdTe 2M/Badpix_mask/bad_pix_from181125.png'

shutil.copyfile(original_path, new_tif_path)

with TiffFile(original_path) as tif:
    page = tif.pages[0]
    offset = page.dataoffsets[0]
    dtype = page.dtype
    shape = page.shape
    original_data = page.asarray()

img = Image.open(png_path).convert('L')
img = img.resize((shape[1], shape[0]))
png_data = np.array(img)
png_data = np.flipud(png_data)

new_data = (png_data > 0).astype(np.uint8)
original_binary = (original_data > 0).astype(np.uint8)
combined_data = ((original_binary | new_data) > 0).astype(dtype)

assert combined_data.shape == shape
assert combined_data.dtype == dtype

with open(new_tif_path, 'r+b') as f:
    f.seek(offset)
    f.write(combined_data.tobytes())

print("New TIFF written with logical OR of original and PNG.")

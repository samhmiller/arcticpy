import matplotlib.pyplot as plt
import numpy as np

from arcticpy.main import add_cti, remove_cti
from arcticpy.roe import ROE
from arcticpy.ccd import CCD
from arcticpy.traps import Trap

# Make input image
image = np.zeros((10, 10))
image[[1, 2, 3], [1, 2, 3]] = 1

# ROE, CCD, and trap species parameters
ccd = CCD(well_fill_power=0.5, full_well_depth=1e5)
roe = ROE()
trap = Trap(density=3, release_timescale=0.5)

# Add cti
added = add_cti(
    image,
    parallel_express=0,
    parallel_roe=roe,
    parallel_ccd=ccd,
    parallel_traps=[trap]
)

# Remove cti
removed = remove_cti(
    image,
    iterations=1,
    parallel_express=0,
    parallel_roe=roe,
    parallel_ccd=ccd,
    parallel_traps=[trap]
)

# Plot output
fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
vmin = np.min((image, added, removed))
vmax = np.max((image, added, removed))

im1 = ax1.imshow(image, cmap='viridis', aspect='equal', vmin=vmin, vmax=vmax)
ax1.set_title('Original')

im2 = ax2.imshow(added, cmap='viridis', aspect='equal', vmin=vmin, vmax=vmax)
ax2.set_title('Add CTI')

im3 = ax3.imshow(removed, cmap='viridis', aspect='equal', vmin=vmin, vmax=vmax)
ax3.set_title('Remove CTI')

fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.85, .15, 0.05, 0.7])
fig.colorbar(im3, cax=cbar_ax)

plt.show()

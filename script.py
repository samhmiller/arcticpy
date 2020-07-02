import matplotlib.pyplot as plt
import numpy as np

from arctic.main import add_cti
from arctic.roe import ROE
from arctic.ccd import CCD
from arctic.traps import Trap

# Make input image
image = np.zeros((100, 100))
image[30, :] = 1

# Instantiate roe
parallel_roe = ROE()
# Instantiate ccd
parallel_ccd = CCD()
# Instantiate trap
parallel_trap = Trap(density=0.5, release_timescale=.50, capture_timescale=0.1)

# Add cti
out = add_cti(image,
              parallel_express=1,
              parallel_roe=parallel_roe,
              parallel_ccd=parallel_ccd,
              parallel_traps=[parallel_trap])

# Plot output
fig, ax = plt.subplots()
im = ax.imshow(image, cmap='viridis', aspect='equal')
fig.colorbar(im, ax=ax)

fig, ax = plt.subplots()
im = ax.imshow(out, cmap='viridis', aspect='equal')
fig.colorbar(im, ax=ax)

plt.show()

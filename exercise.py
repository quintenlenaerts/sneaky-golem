import numpy as np
import matplotlib.pyplot as plt


tue_red = "#C71918"
red_compl = "#18C6C7"

plt.rcParams.update({
    "font.family": "serif",
    "mathtext.fontset": "stix",
    "axes.linewidth": 1.2,
})

coil_values = np.loadtxt("./plasmaex/Poloidal_Mirnov_Coil.txt")
time_values = np.loadtxt("./plasmaex/Poloidal_t.txt")


fig, ax = plt.subplots(figsize=(8.6, 5.6), dpi=160)
ax.plot(time_values, coil_values, lw=1.1, color = tue_red)

plt.show()

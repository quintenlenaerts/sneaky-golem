import os, sys
import download_shot as ds
from shot_data import ShotData

import numpy as np
from scipy import constants

MAJOR_RADIUS = 0.4
MINOR_RADIUS = 0.085

def calc_time(shot_dir, out_dir="time_results", shot_no=51333):
    os.makedirs(out_dir, exist_ok=True)

    shot = ShotData(shot_dir)

    L_p = calc_electron_inductance() + calc_ion_inductance()
    # print(L_p)
    P_mag = L_p * shot["Ip.csv"].iloc[:,1] * shot["dIpdt.csv"].iloc[:,1]
    P_H = shot["U_loop.csv"].iloc[:,1] * shot["Ip.csv"].iloc[:,1] - P_mag
    
    # print(shot["dIpdt.csv"].iloc[:,1])

    print(P_mag)
    print(P_H)


def calc_electron_inductance():
    return constants.mu_0 * MAJOR_RADIUS * np.log(8 * MAJOR_RADIUS / MINOR_RADIUS - 7/2)

def calc_ion_inductance():
    nu = 2 # the peaking factor : assumeing 1 for parabolic or 2 for peaked (more likely to accurately represnet thre reeal worls )
    norm_internal_inductance = np.log(1.65 + 0.89 * nu)
    return constants.mu_0 * MAJOR_RADIUS * norm_internal_inductance / 2 

if __name__ == "__main__":
    num = 51333
    # ds.download_shot(ds.TIME_CONFINEMENT_FILES, num)
    calc_time(f"shot_{num}", shot_no=num)

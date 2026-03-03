import os, sys
import download_shot as ds
from shot_data import ShotData

import numpy as np

# only "unique" functions are implemented here, import any other functions
from validate_plasma import validate_plasma

from plotters.plot_loop_voltage import plot_loop_voltage
from plotters.plot_dBt import plot_dBt_dt


#  helpers

def correct_inf(signal):
    """Inteprolate Inf values"""
    signal = signal.replace([-np.inf, np.inf], np.nan).interpolate()
    return signal


# smaller functions

def compute_chamber_current(shot : ShotData):
    L_chamber = shot["L_chamber"]
    R_chamber = shot["R_chamber"]
    print(L_chamber)
    print(R_chamber)

    return 894455




# main calculation function ie no shot_data yet
def calc_plasma_current(shot_dir, out_dir="last_results", shot_no=2):
    print("\n[] calculting the plasma current in the directoy of shot : " + shot_dir + " ; and outputting to : " + out_dir)

    # creaintg out dir
    os.makedirs(out_dir, exist_ok=True)

    # easier data type
    shot = ShotData(shot_dir)

    if not validate_plasma(shot):
        print("No plasma detected! Aborting.")
        return

    t_CD = float(shot["t_CD"])*1e-6
    t_Bt = float (shot["t_Bt"]) * 1e-6
    offset_sl = slice(None, min(t_Bt, t_CD) - 1e-4)

    t_plasma_start_ms = shot["t_plasma_start"] *1e-3
    t_plasma_end_ms = shot["t_plasma_end"] * 1e-3

    # big voltage things
    loop_voltage = shot["V_loop.csv"]
    polarity_CD = shot["CD_orientation"]

    # print(loop_voltage)
    if polarity_CD != 'CW':            
        loop_voltage *= -1  # make positive

    loop_voltage = correct_inf(loop_voltage)
    loop_voltage.loc[:t_CD] = 0

    plot_loop_voltage(loop_voltage,shot_no, t_plasma_start_ms, t_plasma_end_ms, out_dir + "/loop_voltage.png", show=False)
    plot_loop_voltage(loop_voltage,shot_no, save_path=out_dir + "/loop_voltage_full_range.png", show=False)

    # Ait doing some bt things

    # dBt =   shot["dBt_dt.csv"]
    # polarity_Bt = shot["Bt_orientation"]
    
    # if polarity_Bt != 'CW':     
    #     dBt *= -1  # make positive
    # dBt = correct_inf(dBt)
    # dBt -= dBt.loc[offset_sl].mean()

    dBt = shot["dBt_dt.csv"]          # DataFrame [t, y]
    if shot["Bt_orientation"] != "CW":
        dBt.iloc[:, 1] *= -1          # only flip signal column

    # ax = dBt.plot(grid=True)
    # ax.set(xlabel="Time [s]", ylabel="$dU_{B_t}/dt$ [V]", title="BtCoil_raw signal #{}".format(shot_no))
    plot_dBt_dt(dBt, save_path=out_dir + "/BTcoil_raw.png")




if __name__ == "__main__":
    shot_num = 51333    
    download_shot_data = True

    print("\n[] parsing arugments...")

    # eerst cmd lines parse natuurlijk
    if len(sys.argv) < 2 :
        print("no shot number specified, using default value " + str(shot_num))
        print("specify with: python calc.py <shot_number> <download=1 or 0>")
    else:
        shot_num = sys.argv[1]

    if len(sys.argv) < 3:
        print("no download flag given, downloading the shot again")
        print("specify with <shot_number> <download=1 or 0>")
    else:
        download_shot_data = True if sys.argv[2] == "1" else False

    download_oke = True
    if download_shot_data:
        # using download_shot to download ==> 
        # try:
        print(" ")
        ds.download_shot(ds.PLASMA_CURRENT_FILES, shot_num)
        # except ValueError:
            # download_oke = False
        # else:
            # download_oke = False

    if download_oke:
        shot_dir = f"shot_{shot_num}"
        out_dir = f"shot_{shot_num}_plasma_current"

        calc_plasma_current(shot_dir, out_dir, shot_num)
    else:
        print("Cant download shot_num : " + shot_num)




    
import os, sys
import download_shot as ds



def calc_plasma_current(shot_dir, out_dir="last_results"):
    print("calculting the plasma current in the directoy of shot : " + shot_dir + " ; and outputting to : " + out_dir)

    # creaintg out dir
    os.makedirs(out_dir, exist_ok=True)



if __name__ == "__main__":
    shot_num = 51333    
    download_shot_data = True

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
        try:
            ds.download_shot(ds.PLASMA_CURRENT_FILES, shot_num)
        except ValueError:
            download_oke = False
        else:
            download_oke = False

    if download_oke:
        shot_dir = f"shot_{shot_num}"
        out_dir = f"shot_{shot_num}_plasma_current"

        calc_plasma_current(shot_dir, out_dir)
    else:
        print("Cant download shot_num : " + shot_num)




    
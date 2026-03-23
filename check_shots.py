import os
import shutil
import numpy as np
import matplotlib.pyplot as plt

import download_shot as ds
from shot_data import ShotData

from validate_plasma import validate_plasma, get_plasma_start_and_end_indices

# Signals we require
REQUIRED_SIGNALS = ["Ip.csv", "U_loop.csv"]


def check_signal_availability(shot_dir):
    """
    Check if required signals exist and contain data.
    """
    try:
        shot = ShotData(shot_dir)
    except Exception:
        return False

    for sig in REQUIRED_SIGNALS:
        try:
            data = shot[sig]
            if data is None or len(data) == 0:
                return False
        except Exception:
            return False

    return True


def scan_shots_filtered(shot_numbers, download_missing=True, cleanup=True):
    results = []

    for num in shot_numbers:
        shot_dir = f"shot_{num}"
        exists = os.path.exists(shot_dir)
        downloaded_now = False

        # Download if needed
        if not exists and download_missing:
            try:
                ds.download_shot(ds.TIME_CONFINEMENT_FILES, num)
                exists = True
                downloaded_now = True
            except:
                print(f"Shot {num}: DOWNLOAD FAILED")
                results.append(-1)
                continue

        if not exists:
            print(f"Shot {num}: NOT FOUND")
            results.append(-1)
            continue

        # Load shot
        try:
            shot = ShotData(shot_dir)
        except:
            print(f"Shot {num}: LOAD FAILED")
            results.append(-1)
            continue

        # Check plasma validity
        try:
            p_valid, _, _ = validate_plasma(shot)
        except:
            p_valid = False

        if not p_valid:
            print(f"Shot {num}: NO PLASMA")
            results.append(-1)
        else:
            # Only now check signals
            ok = check_signal_availability(shot_dir)
            results.append(1 if ok else 0)

            print(f"Shot {num}: {'OK' if ok else 'MISSING SIGNALS'} (plasma valid)")

        # Cleanup
        if downloaded_now and cleanup:
            try:
                shutil.rmtree(shot_dir)
            except:
                print(f"Warning: could not delete {shot_dir}")

    return np.array(results)

def plot_filtered_availability(shot_numbers, results):
    shot_numbers = np.array(shot_numbers)
    results = np.array(results)

    valid_mask = results != -1

    filtered_shots = shot_numbers[valid_mask]
    filtered_results = results[valid_mask]

    plt.figure(figsize=(10, 4), dpi=150)
    plt.scatter(filtered_shots, filtered_results, s=10)

    plt.yticks([0, 1], ["Missing signals", "Available"])
    plt.xlabel("Shot number")
    plt.ylabel("Availability (valid plasma only)")
    plt.title("Signal availability for valid plasma shots")

    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    shot_numbers = list(range(50900, 51400))

    availability = scan_shots_filtered(
        shot_numbers,
        download_missing=True,   # download temporarily
        cleanup=True             # delete after checking
    )
    valid = availability != -1
    success_rate = np.sum(availability[valid] == 1) / np.sum(valid)

    print(f"Availability for valid plasma shots: {success_rate:.2%}")
    plot_filtered_availability(shot_numbers, availability)

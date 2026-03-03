import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def plot_dBt_dt(dBt, shot_no=None, t_plasma_start=None, t_plasma_end=None,
                save_path=None, show=True):

    # pandas DataFrame: assume first col = time, second col = signal
    if hasattr(dBt, "iloc") and hasattr(dBt, "shape") and dBt.shape[1] >= 2:
        t = dBt.iloc[:, 0].to_numpy()
        U = dBt.iloc[:, 1].to_numpy()

    # pandas Series: time in index
    elif hasattr(dBt, "index"):
        t = np.asarray(dBt.index.values)
        U = np.asarray(dBt.values)

    # numpy-like 2-col array
    else:
        data = np.asarray(dBt)
        t = data[:, 0]
        U = data[:, 1]

    fig, ax = plt.subplots()
    ax.plot(t, U)
    ax.grid(True)

    title = "BtCoil raw signal" + (f" #{shot_no}" if shot_no is not None else "")
    ax.set(xlabel="Time [s]", ylabel=r"$dU_{B_t}/dt$ [V]", title=title)

    if t_plasma_start is not None and t_plasma_end is not None:
        ax.set_xlim(t_plasma_start, t_plasma_end)

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150)

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig, ax
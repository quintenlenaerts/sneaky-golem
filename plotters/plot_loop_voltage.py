import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def plot_loop_voltage(loop_voltage,
                      shot_no=None,
                      t_plasma_start=None,
                      t_plasma_end=None,
                      save_path=None,
                      show=True):

    data = np.asarray(loop_voltage)
    t = data[:, 0]
    U = data[:, 1]

    fig, ax = plt.subplots()
    ax.plot(t, U)

    title = "Loop voltage $U_l$"
    if shot_no is not None:
        title += f" #{shot_no}"

    ax.set(xlabel="Time [s]", ylabel=r"$U_l$ [V]", title=title)

    if t_plasma_start is not None and t_plasma_end is not None:
        ax.set_xlim(t_plasma_start, t_plasma_end)

    if save_path is not None:
        save_path = Path(save_path)
        if save_path.is_dir() or not save_path.suffix:
            save_path.mkdir(parents=True, exist_ok=True)
            save_file = save_path / f"loop_voltage_{shot_no if shot_no else 'shot'}.png"
        else:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_file = save_path
        fig.savefig(save_file, dpi=150)

    if show:
        plt.show()
    else:
        plt.close(fig) 

    return fig, ax
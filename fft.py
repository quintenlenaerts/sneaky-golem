import numpy as np
import matplotlib.pyplot as plt


tue_red = "#C71918"
red_compl = "#18C6C7"

plt.rcParams.update({
    "font.family": "serif",
    "mathtext.fontset": "stix",
    "axes.linewidth": 1.2,
})


def find_valid_signal(time, signal, threshold_ratio=0.08, smooth_window=200):
    signal = np.asarray(signal)
    time = np.asarray(time)

    # Envelope-like measure
    amp = np.abs(signal)

    # Smooth the absolute value so isolated spikes don't define the region
    window = np.ones(smooth_window) / smooth_window
    amp_smooth = np.convolve(amp, window, mode="same")

    threshold = threshold_ratio * np.max(amp_smooth)
    mask = amp_smooth > threshold

    idx = np.where(mask)[0]
    i0, i1 = idx[0], idx[-1] + 1

    return time[i0:i1], signal[i0:i1], i0, i1


def plot_signal_and_fft(time, signal, threshold_ratio=0.08, smooth_window=200):
    t_valid, s_valid, i0, i1 = find_valid_signal(
        time, signal,
        threshold_ratio=threshold_ratio,
        smooth_window=smooth_window
    )

    print(f"plasma start / end : {time[i0]*1000}/{time[i1]*1000} ms")

    dt = np.mean(np.diff(time))
    f_max = 1 / (2 * dt)
    print(f"highest frequency : {f_max} Hz")

    # Remove DC offset before FFT
    s_fft = s_valid - np.mean(s_valid)

    dt = np.mean(np.diff(t_valid))
    N = len(s_fft)

    fft_vals = np.fft.rfft(s_fft)
    freqs = np.fft.rfftfreq(N, d=dt)
    amplitude = np.abs(fft_vals) / N

    fig, axes = plt.subplots(2, 1, figsize=(5, 4), dpi=160)

    # Raw + selected region
    axes[0].plot(time, signal, lw=1.0/2, color=tue_red, label="raw signal")
    axes[0].axvspan(time[i0], time[i1 - 1], alpha=0.2, color=red_compl, label="valid region")
    axes[0].set_xlabel("time in s")
    axes[0].set_ylabel("Signal")
    # axes[0].set_title("Signal with detected valid region")
    axes[0].legend(frameon=False)

    # FFT of cleaned signal
    axes[1].plot(freqs, amplitude, lw=1.0/2, color=tue_red)
    axes[1].set_xlabel("freq")
    axes[1].set_ylabel("amp")
    # axes[1].set_title("FFT of cleaned signal")
    axes[1].set_xlim(left=0)

    fig.tight_layout()
    plt.show()

    return t_valid, s_valid, freqs, amplitude


coil_values = np.loadtxt("./plasmaex/Poloidal_Mirnov_Coil.txt")
time_values = np.loadtxt("./plasmaex/Poloidal_t.txt")

# coil_values = np.loadtxt("./plasmaex/Toroidal_Mirnov_Coils.txt")
# time_values = np.loadtxt("./plasmaex/Toroidal_t.txt")

plot_signal_and_fft(
    time_values,
    coil_values,
    threshold_ratio=0.08,  
    smooth_window=200       
)
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import integrate, interpolate

import download_shot as ds
from shot_data import ShotData
from validate_plasma import validate_plasma

TIME_BEFORE_TRIGGER_FOR_OFFSET_S = 1e-4


def read_signal_series(shot: ShotData, key: str, name: str) -> pd.Series:
    path = shot.path(key)
    df = pd.read_csv(
        path,
        names=["Time", name],
        comment="#",
        engine="python",
    )
    return df.set_index("Time")[name]



def correct_inf(signal: pd.Series) -> pd.Series:
    return signal.replace([-np.inf, np.inf], np.nan).interpolate()



def calc_plasma_current(shot_dir: str | Path, out_dir: str | Path | None = None) -> pd.DataFrame:
    shot = ShotData(shot_dir)
    shot_dir = Path(shot_dir)
    out_dir = Path(out_dir) if out_dir is not None else shot_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    plasma_result = validate_plasma(shot)
    if not plasma_result[0]:
        raise RuntimeError("Plasma not valid. Aborting.")
    _, t_plasma_start_ms, t_plasma_end_ms = plasma_result

    t_Bt = float(shot["t_Bt"]) * 1e-6
    t_CD = float(shot["t_CD"]) * 1e-6
    offset_end = min(t_Bt, t_CD) - TIME_BEFORE_TRIGGER_FOR_OFFSET_S
    offset_mask = slice(None, offset_end)

    polarity_CD = str(shot["CD_orientation"]).strip()

    loop_voltage = read_signal_series(shot, "V_loop.csv", "V_loop")
    if polarity_CD != "CW":
        loop_voltage *= -1
    loop_voltage = correct_inf(loop_voltage)
    loop_voltage.loc[:t_CD] = 0

    dIpch = read_signal_series(shot, "dIp_dt.csv", "dIp_dt")
    if polarity_CD == "CW":
        dIpch *= -1
    dIpch = correct_inf(dIpch)
    dIpch -= dIpch.loc[offset_mask].mean()
    dIpch.loc[:t_CD] = 0

    K_RogowskiCoil = float(shot["K_RogowskiCoil"])
    R_chamber = float(shot["R_chamber"])
    L_chamber = float(shot["L_chamber"])

    Ipch = pd.Series(
        integrate.cumulative_trapezoid(dIpch, x=dIpch.index, initial=0) * K_RogowskiCoil,
        index=dIpch.index,
        name="Ipch",
    )

    U_l_func = interpolate.interp1d(
        loop_voltage.index,
        loop_voltage.values,
        bounds_error=False,
        fill_value=(loop_voltage.iloc[0], loop_voltage.iloc[-1]),
    )

    def dIch_dt(t: float, ich: np.ndarray) -> np.ndarray:
        return (U_l_func(t) - R_chamber * ich) / L_chamber

    t_eval = loop_voltage.index.to_numpy()
    t_span = (float(t_eval[0]), float(t_eval[-1]))
    solution = integrate.solve_ivp(dIch_dt, t_span, [0.0], t_eval=t_eval)

    if len(solution.y[0]) != len(t_eval):
        ich_values = np.interp(t_eval, solution.t, solution.y[0])
    else:
        ich_values = solution.y[0]

    Ich = pd.Series(ich_values, index=loop_voltage.index, name="Ich")
    Ip = (Ipch - Ich).rename("Ip")

    df_out = pd.concat([loop_voltage.rename("U_loop"), Ipch, Ich, Ip], axis="columns")
    df_out.index.name = "time_s"
    df_out.insert(0, "time_ms", df_out.index.to_numpy() * 1e3)

    plasma_mask = (df_out["time_ms"] >= t_plasma_start_ms) & (df_out["time_ms"] <= t_plasma_end_ms)
    df_plasma = df_out.loc[plasma_mask].copy()

    csv_path = out_dir / "Ip.csv"
    df_out.loc[:, ["time_ms", "Ip"]].to_csv(csv_path, index=False)

    # plasma_csv_path = out_dir / "Ip_plasma_only.csv"
    # df_plasma.loc[:, ["time_ms", "Ip"]].to_csv(plasma_csv_path, index=False)

    print(f"Saved full plasma current CSV to: {csv_path}")
    # print(f"Saved plasma-window current CSV to: {plasma_csv_path}")
    print(
        "Ip summary during plasma [A]: "
        f"min={df_plasma['Ip'].min():.3f}, "
        f"max={df_plasma['Ip'].max():.3f}, "
        f"mean={df_plasma['Ip'].mean():.3f}"
    )

    return df_out



def handle_shot_download() -> str:
    shot_no = "51333"
    if len(sys.argv) > 1:
        shot_no = str(sys.argv[1])

    should_download = True
    if len(sys.argv) > 2:
        should_download = sys.argv[2] == "1"

    print(f"calculating plasma current for shot {shot_no} | downloading: {should_download}")
    if should_download:
        ds.download_shot(ds.PLASMA_CURRENT_2_FILES, shot_no)

    return shot_no


if __name__ == "__main__":
    shot_no = handle_shot_download()
    calc_plasma_current(f"shot_{shot_no}")

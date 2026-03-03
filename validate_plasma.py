from shot_data import ShotData


def validate_plasma(shot : ShotData):
    """
        Are gonna make sure that the plasma is alive and well ie a lifetime of more then 0s.
    """

    if (shot["b_plasma"] != 1):
        return False

    t_plasma_start = shot["t_plasma_start"]
    t_plasma_end = shot["t_plasma_end"]
    plasma_lifetime = shot["t_plasma_duration"]
    print(f"plasma lifetime of {plasma_lifetime:.1f} ms, from {t_plasma_start:.1f} ms to {t_plasma_end:.1f} ms")

    return True
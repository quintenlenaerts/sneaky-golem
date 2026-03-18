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
    print(f"[^-^] plasma lifetime of {plasma_lifetime:.1f} ms, from {t_plasma_start:.1f} ms to {t_plasma_end:.1f} ms")

    return True, t_plasma_start, t_plasma_end


def get_plasma_start_and_end_indices(plasma_start,plasma_end, time_arr, accuracy=1e-4):
    """
        Given values shuol be floats or else.

        Time array should be from the shot
    """
    start_index, end_index = 0

    for i in range(len(time_arr)):
        time_step = time_arr[i]
        if abs(plasma_start - time_step) <= accuracy:
            start_index = i
        
        if abs(plasma_end - time_step) <= accuracy:
            end_index = i

    return start_index, end_index
        




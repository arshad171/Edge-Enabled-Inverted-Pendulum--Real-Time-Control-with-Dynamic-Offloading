from perx.ctypes import *


def get_shape_scale(app_name) -> Tuple[int, int]:
    mem = APP_MEMS[app_name]

    scale = min(mem / AVAILABLE_MEM, MAX_SHAPE_SIZE)

    return scale

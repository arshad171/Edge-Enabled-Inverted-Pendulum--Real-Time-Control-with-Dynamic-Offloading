from typing import Tuple

AVAILABLE_MEM = 4 # GB

APP_MEMS = {
    "visual-servo": 0.3,
    "iclf-efnet": 1.3,
    "text-tbert": 0.7,
}

APP_SCALES = {
    "visual-servo": 0.9,
    "iclf-efnet": 2,
    "text-tbert": 1.4,
}

APP_REVS = {
    "visual-servo": 0.5,
    "iclf-efnet": 3,
    "text-tbert": 2,
}

MAX_SHAPE_SIZE = 75

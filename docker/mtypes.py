from typing import Any, NamedTuple, List, Dict, Optional

HOME_PATH = "/home/arshad/code/Edge-Enabled-Inverted-Pendulum--Real-Time-Control-with-Dynamic-Offloading/"

ARRIVAL_RATES = [20, 100]  # per instance
NUM_INSTANCES = [2, 10]

APPLICATIONS = [
    "visual-servo",
    "iclf-efnet",
    "text-tbert"
]

APP_MEM_REQS = {
    "visual-servo": 0.3,
    "efnet": 1.3,
    "tbert": 0.7,
}

APP_AVG_ARRIVALS = {
    "visual-servo": 2,
    "iclf-efnet": 1,
    "text-tbert": 1,
}

class TenantRequest(NamedTuple):
    ### request paramters
    id: int
    application: str
    # avg. per instance
    arrival_rate: float
    num_instances: int
    payment: float = 0.0
    delay: float = 0.0
    sla_type: int = 1

    ### additional attrs for processing
    port: int = None
    pids: List = []


def get_app_mem_req(app):
    mem_limit = APP_MEM_REQS.get(app, None)
    if mem_limit is not None:
        mem_limit = round(mem_limit * 1.2, 1)

    return mem_limit

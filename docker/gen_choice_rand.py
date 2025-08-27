import json
import os
import random
import numpy as np
import argparse
from docker.mtypes import *
# from docker.utils import get_app_arrival_rate, get_app_num_instances

OUT_FILE = "tenant_requests.json"
MIN_NUM_INSTANCES = min(NUM_INSTANCES)
# MIN_MEM_REQ = min(list(APP_MEM_REQS.values()))

parser = argparse.ArgumentParser(description="kwargs")
parser.add_argument("--out-folder", type=str, help="output folder to dump the config", default=".")
parser.add_argument("--config", type=str, help="explicit config to deploy, else random_u", default=None)
parser.add_argument("--rand-app-cat", type=str, help="v1|v2", default="v1")

args = parser.parse_args()
arg_out_folder = args.out_folder
arg_config = args.config
arg_rand_app_cat = args.rand_app_cat


tenant_requests: List[TenantRequest] = []

# available_capacity = 40
# cap1: 24 - 32
# cap2: 16 - 24
# cap3: 8 - 16
# available_capacity = random.randint(8, 16)
available_capacity = 4
print("capacity limit", available_capacity)

if arg_config:
    deployments = arg_config.split(",")
    tenant_requests = []
    id = 0
    for deployment in deployments:
        app_deployment_config = deployment.split("|")
        app_deployment_config_dict = {}
        for config in app_deployment_config:
            key, val = config.split("=")
            app_deployment_config_dict[key] = val
        
        app = app_deployment_config_dict["app"]
        lam = float(app_deployment_config_dict["lam"])
        ni = int(app_deployment_config_dict["ni"])

        print(app, lam, ni)

        # if lam is None and ni != "none":
        #     ni = float(ni)

        #     lam = get_app_arrival_rate(app, ni, exact=True)
        # elif lam is not None and ni == "none":
        #     lam = float(lam)

        #     ni = get_app_num_instances(app, lam)

        # else:
        #     lam = float(lam)
        #     ni = float(ni)

        # deployments_list.append(app_deployment_config_dict)
        tenant_requests.append(TenantRequest(
            id=id,
            application=app,
            arrival_rate=lam,
            num_instances=ni,
        ))

        id += 1

else:
    id = 0
    for _ in range(500):
        if (available_capacity <= 0):
            break

        t_app = random.choice(APPLICATIONS)

        t_arrival_rate = random.randint(*ARRIVAL_RATES)
        # t_arrival_rate = int(t_arrival_rate / 2)
        t_num_instances = int(random.randint(*NUM_INSTANCES))
        # t_num_instances = max(1, int(t_num_instances / 2))
        t_arrival_rate /= t_num_instances
        

        if available_capacity - t_num_instances * get_app_mem_req(t_app) <= 0:
            continue

        id += 1
        
        tenant_requests.append(TenantRequest(id=id, application=t_app, arrival_rate=t_arrival_rate, num_instances=t_num_instances))

        # available_capacity -= t_num_instances
        available_capacity -= t_num_instances * get_app_mem_req(t_app)

    print(f"{available_capacity=}")
    total_mem = 0
    total_ni = 0
    for req in tenant_requests:
        print(f"{req.application:<10} \t {req.num_instances:>5}")
        total_mem += req.num_instances *  get_app_mem_req(req.application)
        total_ni += req.num_instances

    print(f"{total_mem=} | {total_ni=}")

out_data = {
    "tenant_requests": [req._asdict() for req in tenant_requests]
    # "tenant_requests": tenant_requests
}

json.dump(out_data, open(os.path.join(arg_out_folder, "tenant_requests.json"), "w"), indent=4)

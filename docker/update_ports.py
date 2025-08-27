from collections import defaultdict
import itertools
import os
import subprocess
import json
import sys
import pandas as pd
import numpy as np

import time
import requests
import aiohttp
import asyncio
import time
import random
import argparse
from concurrent.futures import ThreadPoolExecutor

from docker.mtypes import *

parser = argparse.ArgumentParser(description="kwargs")

parser.add_argument("--out-folder", type=str, help="output folder", default="output")
args = parser.parse_args()
arg_out_folder = args.out_folder

files = [f for f in os.listdir(HOME_PATH) if f.endswith(".url.log")]

data = json.load(open(os.path.join(arg_out_folder, "tenant_requests.json")))
tenant_requests: List[TenantRequest] = [
    TenantRequest(**req) for req in data["tenant_requests"]
]

# for tenant in tenant_requests:
for ix in range(len(tenant_requests)):
    tenant = tenant_requests[ix]
    print(tenant.application)
    with open(f"{HOME_PATH}/{tenant.application}.url.log", "r") as file:
        url = file.readline()
        url = url.strip()

        print(url)
        port = int(url.split(":")[-1])

        tenant = tenant._replace(port=port)

    tenant_requests[ix] = tenant

out_data = {
    "tenant_requests": [req._asdict() for req in tenant_requests]
    # "tenant_requests": tenant_requests
}

json.dump(out_data, open(os.path.join(arg_out_folder, "tenant_requests.json"), "w"), indent=4)

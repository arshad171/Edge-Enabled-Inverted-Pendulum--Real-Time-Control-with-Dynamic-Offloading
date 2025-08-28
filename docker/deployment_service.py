import shutil

import yaml
from flask import Flask, request, jsonify
import subprocess
import json
import os
from docker.mtypes import *
from docker.utils import get_sample_kube_dep

OUT_FOLDER = "/home/arshad/code/Edge-Enabled-Inverted-Pendulum--Real-Time-Control-with-Dynamic-Offloading/live_deps"

app = Flask(__name__)

@app.route('/deploy', methods=['POST'])
def deploy():

    data = request.get_json()
    deployments = data["deployments"]

    tenant_requests: List[TenantRequest] = []
    for ix, (app, replicas) in enumerate(deployments.items()):
        if replicas == 0:
            continue

        req = TenantRequest(
            id=ix,
            application=app,
            arrival_rate=APP_AVG_ARRIVALS[app],
            num_instances=replicas,
        )

        tenant_requests.append(req)
    

    out_data = {
        "tenant_requests": [req._asdict() for req in tenant_requests]
        # "tenant_requests": tenant_requests
    }

    json.dump(out_data, open(os.path.join(OUT_FOLDER, "tenant_requests.json"), "w"), indent=4)

    dir_path = f"{OUT_FOLDER}/kube_deps_p5"

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

    os.mkdir(dir_path)

    kube_deps = []
    port_counter = 30001
    emul_tenants = []
    for tenant_request in tenant_requests:
        t_id = tenant_request.id
        t_app = tenant_request.application
        t_num_instances = tenant_request.num_instances

        if mem_limit := APP_MEM_REQS.get(t_app, None):
            mem_limit = round(mem_limit * 1.2, 1)
        else:
            mem_limit = None
        print(f"{t_app}, {mem_limit=}")
        kube_dep = get_sample_kube_dep(t_app, t_num_instances, port_counter, t_id, env_proc_title=f"kube_{t_id}", memory_limit=mem_limit)
        # kube_dep = get_sample_kube_dep(t_app, t_num_instances, port_counter, t_id, env_proc_title=f"kube_{t_id}")

        emul_tenant = tenant_request._replace(port=port_counter)
        emul_tenants.append(emul_tenant)

        port_counter += 1
        kube_deps.extend(kube_dep)


    with open(os.path.join(dir_path, f"kube_deps.yaml"), "w") as out_file:
        for i, doc in enumerate(kube_deps):
            if i > 0:
                out_file.write('---\n')
            yaml.safe_dump(doc, out_file)

    out_data = {
        "tenant_requests": [req._asdict() for req in emul_tenants]
        # "tenant_requests": tenant_requests
    }

    json.dump(out_data, open(os.path.join(OUT_FOLDER, "tenant_requests.json"), "w"), indent=4)

    try:
        result = subprocess.run(
            ["./docker/deployment_apply.bash"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout

        bg_process = subprocess.Popen([
            "/home/arshad/anaconda3/envs/pa_res_alloc/bin/python",
            "-m", "docker.emulate_tenants",
            "--out-folder=/home/arshad/code/Edge-Enabled-Inverted-Pendulum--Real-Time-Control-with-Dynamic-Offloading/live_deps/"
        ])


        return jsonify({"status": "ok", "script_output": output}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "stderr": e.stderr}), 500
@app.route('/clear', methods=['get'])
def clear():
    print("/clear:")
    try:
        result = subprocess.run(
            ["./docker/deployment_clear.bash"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout
        return jsonify({"status": "ok", "script_output": output}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "stderr": e.stderr}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
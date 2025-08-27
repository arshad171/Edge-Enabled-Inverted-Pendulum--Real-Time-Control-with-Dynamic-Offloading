import random
import yaml

from docker.mtypes import *

a_ports = {
    "visual-servo": 8000,
    "iclf-efnet": 8001,
    "text-tbert": 8007,
}

c_ports = {
    "visual-servo": 30000,
    "iclf-efnet": 30001,
    "text-tbert": 30007,
}


# def get_app_arrival_rate(app, ni, exact=False):
#     app_arrival = APP_TASK_ARRIVAL_RATES_E[app] * ni

#     if not exact:
#         ll = max(1, int(app_arrival * 0.75))
#         ul = max(1, int(app_arrival * 1.25))
#         app_arrival = random.randint(ll, ul)

#     return app_arrival


# def get_app_num_instances(app, arrival_rate):
#     app_arrival = APP_TASK_ARRIVAL_RATES_E[app] * 0.5

#     ni = arrival_rate / app_arrival

#     ll = max(1, int(ni))
#     ul = max(1, int(ni * 2.5))
#     ni = random.randint(ll, ul)

#     return ni


def get_sample_kube_dep(
    app, replicas, port, group_ix, env_proc_title=None, memory_limit=None
):
    with open(
        f"/Users/arshadjaveed/My Data/Workspace/Edge-Enabled-Inverted-Pendulum--Real-Time-Control-with-Dynamic-Offloading/docker/kube_dep1.yaml",
        "r",
    ) as file:
        docs = list(yaml.safe_load_all(file))

        docs[0]["spec"]["replicas"] = int(replicas)

        docs[0]["metadata"]["name"] = f"{app}-deployment-{group_ix}"
        docs[0]["spec"]["selector"]["matchLabels"]["app"] = f"{app}"
        docs[0]["spec"]["selector"]["matchLabels"]["group"] = f"group-{group_ix}"
        docs[0]["spec"]["template"]["metadata"]["labels"]["app"] = f"{app}"
        docs[0]["spec"]["template"]["metadata"]["labels"]["group"] = f"group-{group_ix}"
        docs[0]["spec"]["template"]["spec"]["containers"][0]["name"] = f"{app}"
        docs[0]["spec"]["template"]["spec"]["containers"][0]["image"] = f"{app}"
        docs[0]["spec"]["template"]["spec"]["containers"][0]["ports"][0][
            "containerPort"
        ] = a_ports[app]

        if memory_limit is not None:
            docs[0]["spec"]["template"]["spec"]["containers"][0]["resources"] = {
                "limits": {"memory": f"{int(memory_limit * 1000)}Mi"}
            }

        # docs[1]["metadata"]["name"] = f"{app}-service-{group_ix}"
        docs[1]["metadata"]["name"] = f"{app}-service"
        docs[1]["spec"]["selector"]["app"] = f"{app}"
        docs[1]["spec"]["selector"]["group"] = f"group-{group_ix}"
        docs[1]["spec"]["ports"][0]["port"] = a_ports[app]
        docs[1]["spec"]["ports"][0]["targetPort"] = a_ports[app]
        docs[1]["spec"]["ports"][0]["nodePort"] = port

        if env_proc_title:
            docs[0]["spec"]["template"]["spec"]["containers"][0]["env"] = [
                {"name": "PROC_TITLE", "value": env_proc_title}
            ]

    return docs

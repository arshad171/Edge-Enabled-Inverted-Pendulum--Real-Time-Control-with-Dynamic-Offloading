import subprocess
import sys

ML_MODEL_CONFIGS = [
    {"name": "visual-servo", "port": "8000", "module": "visual_servo"},
    {"name": "iclf-efnet", "port": "8001", "module": "ml_iclf_efnet"},
    {"name": "text-tbert", "port": "8007", "module": "ml_text_tbert"},
]

for config in ML_MODEL_CONFIGS:
    name = config["name"]
    port = config["port"]
    module = config["module"]

    print("*" * 10, "building", name)

    subprocess.run(["rm", "-rf", "module"])
    subprocess.run(["cp", "-r", f"./{module}", "module"])

    result = subprocess.run(
        [
            "docker",
            "build",
            "--build-arg",
            f"ARG_MODULE={module}",
            "--build-arg",
            f"APP_PORT={port}",
            "--build-arg",
            f"APP_MODEL_URL={name}",
            "--build-arg",
            f'ARG_TF_USE_LEGACY_KERAS={config.get("TF_USE_LEGACY_KERAS", "0")}',
            "--build-arg",
            f"APP_MODEL_BATCH_SIZE=16",
            "--build-arg",
            f"USE_GPU=0",
            "-t",
            f"{name}",
            ".",
        ],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    subprocess.run(["rm", "-rf", "module"])

    print(result)

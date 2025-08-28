#!/bin/bash

kubectl apply -f "/home/arshad/code/Edge-Enabled-Inverted-Pendulum--Real-Time-Control-with-Dynamic-Offloading/live_deps/kube_deps_p5" -n background;
sleep 10;
kubectl get pods -n background;

# ps -eo pid,cmd | grep my_emulate_tenants | grep -v "grep"


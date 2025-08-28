#!/bin/bash
kubectl delete deployments --all -n background;
kubectl delete services --all -n background;

# pkill $(pgrep "my_emulate_tenants");

# minikube start --driver docker --container-runtime docker --cpus 16 --gpus all;
minikube start --cpus 6 --memory 6g; 
# minikube addons enable dashboard;
minikube addons enable metrics-server;

conda activate pi_env;

# minikube -p minikube docker-env;
eval $(minikube -p minikube docker-env);

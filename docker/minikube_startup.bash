# minikube start --driver docker --container-runtime docker --cpus 16 --gpus all;
# minikube start --cpus 6 --memory 6g; 
minikube start --cpus 32 --memory 40g;

# minikube addons enable dashboard;
minikube addons enable metrics-server;

# conda activate pi_env;
conda activate pa_res_alloc;

# minikube -p minikube docker-env;
eval $(minikube -p minikube docker-env);

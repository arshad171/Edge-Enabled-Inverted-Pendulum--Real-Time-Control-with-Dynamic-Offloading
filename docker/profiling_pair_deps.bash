ulimit -n 5000;

# apps1=("visual-servo")
# apps2=("visual-servo" "iclf-efnet" "text-tbert")
# lams=(1.0 2.0 4.0 6.0)
apps1=("visual-servo")
# apps2=("visual-servo" "iclf-efnet" "text-tbert")
apps2=("text-tbert")
nis_vs=(1 4 8 16 32)
nis_ie=(1 4 8 16 24)
nis_tt=(1 4 8 16 32)


lam_vs=(1 2 5 10)
lam_ie=(1 2 5 10)
lam_tt=(1 2 5 10)


OUT_FOLDER_1="/home/arshad/code/Edge-Enabled-Inverted-Pendulum--Real-Time-Control-with-Dynamic-Offloading/data/pair"
mkdir -p "$OUT_FOLDER_1"

for app1 in "${apps1[@]}"; do
    for app2 in "${apps2[@]}"; do
        if [[ "$app2" == "visual-servo" ]]; then
            nis=("${nis_vs[@]}")
            lams=("${lam_vs[@]}")
        elif [[ "$app2" == "iclf-efnet" ]]; then
            nis=("${nis_ie[@]}")
            lams=("${lam_ie[@]}")
        elif [[ "$app2" == "text-tbert" ]]; then
            nis=("${nis_tt[@]}")
            lams=("${lam_tt[@]}")
        else
            echo "no match"
        fi

        for ni in "${nis[@]}"; do
            for lam in "${lams[@]}"; do
                echo "$app1 - $app2 ($ni, $lam)"
                OUT_FOLDER_2="$OUT_FOLDER_1/${app1}_${app2}/$ni/$lam"
                mkdir -p "$OUT_FOLDER_2";
                echo $OUT_FOLDER_2

                kubectl delete deployments --all -n default;
                kubectl delete services --all -n default;

                sleep 3;

                python -m docker.gen_choice_rand --out-folder="$OUT_FOLDER_2" --config="app=$app1|lam=1|ni=1,app=$app2|lam=$lam|ni=$ni";
                python -m docker.gen_deps_rand --out-folder="$OUT_FOLDER_2";
                kubectl apply -f "$OUT_FOLDER_2/kube_deps_p5";

                sleep 25;

                # minikube service "$app1-service" --url > "$app1.url.log" &
                # pid1=$!
                # minikube service "$app2-service" --url > "$app2.url.log" &
                # pid2=$!

                # echo "$app2-service"
                # echo $pid1
                # echo $pid2
                # sleep 3;

                # python -m docker.update_ports --out-folder="$OUT_FOLDER_2";

                # sleep_time=$(( ni + 12 ))
                # sleep "$sleep_time"

                # # python -m docker.proc_mon --out-folder="$OUT_FOLDER_2";
                python -m docker.emulate_tenants --out-folder="$OUT_FOLDER_2";
                # # python -m docker.parse_proc_events --out-folder="$OUT_FOLDER_2";

                # kill $pid1;
                # kill $pid2;
                # rm ./*.url.log;
            done
        done
    done
done
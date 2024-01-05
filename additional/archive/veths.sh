#!/bin/bash

container_names=("httpd" "app1" "db")

for container_name in "${container_names[@]}"; do
    pid=$(docker inspect -f '{{.State.Pid}}' "$container_name")
    iflink=$(sudo nsenter -t $pid -n ip link show eth0 | awk '{print $1}' | sed -n '1s/://gp')
    
    for veth in /sys/class/net/veth*/iflink; do
        if [[ "$(cat $veth)" == "$iflink" ]]; then
            veth_name=$(basename $(dirname $veth))
            echo "Container '$container_name' is using interface $veth_name"
            break
        fi
    done
done


for j in `seq 4 20`; do for i in `seq 1 100`; do sudo ip addr add dev lo 172.20.$j.$i/32 ; done ; done


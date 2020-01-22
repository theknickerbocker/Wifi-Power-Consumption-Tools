# Navigate to the directory where udpsender is located
cd /data/local/tmp

# Check for the correct number of arguments
if [[ "$#" != 3 ]];
then
    echo "Enter as arguments: num_cores core_freq src_rate"
    exit
fi

num_cores=$1
core_freq=$2
src_rate=$3

# Set number of cores online and core frequency and print results
./set_cpus.sh $num_cores $core_freq
./check_cpus.sh
echo "CPUS SET"

# Set network config and print results
./setNetwork.sh
ifconfig wlan0
echo "NETWORK SET"

# Set filenames, either by default format or the optional name entered as an arg
ip=$3
lock_name="power_measure_lock"
run_time=60

# cap_name=""
log_path=""

cpu_spec_identifier=$num_cores"core_"$core_freq"khz"
cpu_spec_path="data/"$cpu_spec_identifier

# udp_dir_name=$cpu_spec_path"/udp_caps/"
iperf_dir_name=$cpu_spec_path"/iperf_logs/"

# Check if the directories data/udp_caps and data/iperf_logs exist, if not then make
if [ ! -d "data" ];
then
    mkdir "data"
fi
if [ ! -d $cpu_spec_path ];
then
    mkdir $cpu_spec_path
fi
# if [ ! -d $udp_dir_name ];
# then
#     mkdir $udp_dir_name
# fi
if [ ! -d $iperf_dir_name ];
then
    mkdir $iperf_dir_name
fi

    

    # cap_name+=$udp_dir_name
    log_name+=$iperf_dir_name

echo $lock_name > /sys/power/wake_lock
# Delay 20 seconds so that monsoon power monitor can begin measuments preemptively
sleep 30

# Array of source rates to be measured

# Run udpsender for every desired source rate
bandwidth=$((1470 * 8 * $src_rate))

for i in `seq 1 3`;
do
    cur_log_name=$log_name$cpu_spec_identifier"_"$src_rate"src_v"$i".log"
    # cur_cap_name=$cap_name$cpu_spec_identifier"_"${source_rates[$i]}"src.pcap"


    time=$(echo $EPOCHREALTIME)
    echo "Start: "$time > $cur_log_name
    ./iperf -u -c 192.168.0.2 -b $bandwidth -t $run_time >> $cur_log_name
    time=$(echo $EPOCHREALTIME)
    echo "End: "$time >> $cur_log_name
sleep 3
done

echo $lock_name > /sys/power/wake_unlock

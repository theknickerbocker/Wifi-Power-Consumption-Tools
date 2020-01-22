#! /bin/bash

source_rates=(1 3 5 6 10 15 25 35 55 70 95 100 200 400 800 1200 1500 1800 3000 4000 6000 8000 10000
12000 14000 16000)
length=${#source_rates[@]}
end_index=`expr $length - 1`

for i in `seq 0 $end_index`;
do
    src_rate=${source_rates[$i]}
    filename="4core_2457600khz_"$src_rate"src.log"

    start=$(sed '1q;d' $filename)
    end=$(sed '10q;d' $filename)
    echo $start","$end
done
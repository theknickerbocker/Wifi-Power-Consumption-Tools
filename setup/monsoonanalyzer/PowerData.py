import csv
import bisect
from monsoonanalyzer.PowerInstance import PowerInstance
from monsoonanalyzer.PowerSegment import PowerSegment

class PowerData():

    def __init__(self, cpu_cores, cpu_freq, filename, offset=0):
        self.cpu_cores = cpu_cores
        self.cpu_freq = cpu_freq
        self.power_instance_list = []
        self.power_segment_dict = {}

        with open(filename, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            csv_reader.__next__()

            for entry in csv_reader:
                timestamp = offset + (float(entry[0]) * 1000000)
                
                # current = float(entry[1])
                power = float(entry[1])
                # voltage = float(entry[3])

                power_cap = PowerInstance(timestamp, 0, power, 0)
                bisect.insort(self.power_instance_list, power_cap)

    def segment_by_transmit_data(self, transmit_data, baseline):
        src_rates = transmit_data.src_rates
        src_rate_index = 0
        current_transmission = transmit_data.transmit_segment_dict[src_rates[src_rate_index]]
        segment_power = 0
        power_measument_count = 0
        transmission_active = False

        for power_instance in self.power_instance_list:
            if transmission_active:
                if power_instance.timestamp <= current_transmission.end_time:
                    segment_power += power_instance.power
                    power_measument_count += 1
                else:
                    avg_power = (segment_power / power_measument_count) - baseline
                    self.power_segment_dict[src_rates[src_rate_index]] = PowerSegment(
                        current_transmission.start_time,
                        current_transmission.end_time,
                        avg_power)
                        
                    src_rate_index += 1
                    if src_rate_index >= len(src_rates):
                        break
                    
                    current_transmission = transmit_data.transmit_segment_dict[src_rates[src_rate_index]]
                    segment_power = 0
                    power_measument_count = 0
                    transmission_active = False

            elif  current_transmission.start_time <= power_instance.timestamp:
                transmission_active = True
                power_measument_count += 1
                segment_power += power_instance.power

        

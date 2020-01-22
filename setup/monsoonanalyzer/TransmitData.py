import csv
from monsoonanalyzer import TransmitSegment

class TransmitData():

    def __init__(self, cpu_cores, cpu_freq, filename):
        self.cpu_cores = cpu_cores
        self.cpu_freq = cpu_freq
        self.src_rates = []
        self.transmit_segment_dict = {}

        with open(filename, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')

            for entry in csv_reader:
                expected_src_rate = int(entry[0])
                start_time = int(float(entry[1]))
                end_time = int(float(entry[2]))
                total_time = int(float(entry[3]))
                packets_sent = int(entry[4])

                self.transmit_segment_dict[expected_src_rate] = TransmitSegment(
                    expected_src_rate,
                    start_time,
                    end_time,
                    total_time,
                    packets_sent)
        
        self.src_rates = sorted(list(self.transmit_segment_dict.keys()))

    # def normalize_timing(self, full_transmission_end_time):
    #     cur_time = full_transmission_end_time
    #     for src_rate in reversed(self.src_rates):
    #         transmit_segment = self.transmit_segment_dict[src_rate]
    #         transmit_segment.end_time = cur_time

    #         cur_time -= transmit_segment.total_time
    #         transmit_segment.start_time = cur_time

    #         cur_time -= 3000000

    def normalize_timing(self, full_transmission_end_time):
        cur_time = full_transmission_end_time
        for i,src_rate in enumerate(reversed(self.src_rates)):
            transmit_segment = self.transmit_segment_dict[src_rate]
            pred_diff = 0
            if i != len(self.src_rates) - 1:
                pred_segment = self.transmit_segment_dict[self.src_rates[len(self.src_rates) - i - 2]]
                pred_diff = transmit_segment.start_time - pred_segment.end_time

            transmit_segment.end_time = cur_time

            cur_time -= transmit_segment.total_time
    
            transmit_segment.start_time = cur_time

            cur_time -= pred_diff
